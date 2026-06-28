import json
import subprocess
from typing import Optional
from kubernetes import client as k8s_client, config as k8s_config
from kubernetes.client.rest import ApiException
from ksm_core.config import settings


class K8sClient:
    def __init__(self, env):
        self.env = env
        self._api_client: Optional[k8s_client.CoreV1Api] = None

    def _get_sdk_client(self) -> k8s_client.CoreV1Api:
        if self._api_client is not None:
            return self._api_client
        try:
            kubeconfig_dict = json.loads(self.env.kubeconfig)
            k8s_config.load_kube_config_from_dict(kubeconfig_dict)
        except (json.JSONDecodeError, ValueError):
            import tempfile, os
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
            tmp.write(self.env.kubeconfig)
            tmp.close()
            k8s_config.load_kube_config(config_file=tmp.name)
            os.unlink(tmp.name)
        self._api_client = k8s_client.CoreV1Api()
        return self._api_client

    def _use_kubectl(self, args: list[str]) -> str:
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        tmp.write(self.env.kubeconfig)
        tmp.close()
        try:
            result = subprocess.run(
                ["kubectl", f"--kubeconfig={tmp.name}"] + args,
                capture_output=True, text=True, timeout=settings.K8S_SDK_TIMEOUT,
            )
            if result.returncode != 0:
                raise RuntimeError(f"kubectl error: {result.stderr}")
            return result.stdout
        finally:
            os.unlink(tmp.name)

    async def get_namespaces(self) -> list[dict]:
        try:
            v1 = self._get_sdk_client()
            ns_list = v1.list_namespace()
            return [{"name": ns.metadata.name, "status": ns.status.phase} for ns in ns_list.items]
        except ApiException as e:
            if self.env.k8s_sdk_mode == "sdk":
                raise RuntimeError(f"K8s API error: {e}")
            output = self._use_kubectl(["get", "namespaces", "-o", "json"])
            data = json.loads(output)
            return [{"name": item["metadata"]["name"], "status": item["status"]["phase"]} for item in data["items"]]

    async def list_secrets(self, namespace: str) -> list[dict]:
        try:
            v1 = self._get_sdk_client()
            secrets = v1.list_namespaced_secret(namespace)
            return [{
                "name": s.metadata.name,
                "type": s.type,
                "keys": list(s.data.keys()) if s.data else [],
            } for s in secrets.items]
        except ApiException as e:
            if self.env.k8s_sdk_mode == "sdk":
                raise RuntimeError(f"K8s API error: {e}")
            output = self._use_kubectl(["get", "secrets", "-n", namespace, "-o", "json"])
            data = json.loads(output)
            return [{
                "name": item["metadata"]["name"],
                "type": item["type"],
                "keys": list(item.get("data", {}).keys()),
            } for item in data["items"]]

    async def get_secret_value(self, namespace: str, secret_name: str, key: str) -> str:
        try:
            v1 = self._get_sdk_client()
            secret = v1.read_namespaced_secret(secret_name, namespace)
            if secret.data and key in secret.data:
                import base64
                return base64.b64decode(secret.data[key]).decode("utf-8", errors="replace")
            raise KeyError(f"Key '{key}' not found in secret '{secret_name}'")
        except ApiException as e:
            if self.env.k8s_sdk_mode == "sdk":
                raise RuntimeError(f"K8s API error: {e}")
            output = self._use_kubectl([
                "get", "secret", secret_name, "-n", namespace,
                "-o", f"jsonpath={{.data.{key}}}",
            ])
            import base64
            return base64.b64decode(output.strip()).decode("utf-8", errors="replace")

    async def check_health(self) -> dict:
        try:
            v1 = self._get_sdk_client()
            version = v1.get_code()
            nodes = v1.list_node()
            return {
                "status": "ok",
                "version": version.git_version,
                "node_count": len(nodes.items),
            }
        except ApiException as e:
            return {"status": "error", "message": str(e)}
