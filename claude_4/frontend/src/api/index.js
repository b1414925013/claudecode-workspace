import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export default {
  search(keyword, platform = 'all') {
    return api.get('/search', { params: { q: keyword, platform } })
  },
  getPlayUrl(songId, platform) {
    return api.get(`/play/${songId}`, { params: { platform } })
  },
  getLyrics(songId, platform) {
    return api.get(`/lyrics/${songId}`, { params: { platform } })
  },
  getRankings(platform = 'netease', type = 'hot') {
    return api.get('/rankings', { params: { platform, type } })
  }
}
