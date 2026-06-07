import { defineStore } from 'pinia'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    playlists: JSON.parse(localStorage.getItem('playlists') || '[]'),
    favorites: JSON.parse(localStorage.getItem('favorites') || '[]')
  }),
  actions: {
    addToFavorites(song) {
      if (!this.favorites.find(s => s.id === song.id)) {
        this.favorites.push(song)
        localStorage.setItem('favorites', JSON.stringify(this.favorites))
      }
    },
    removeFromFavorites(songId) {
      this.favorites = this.favorites.filter(s => s.id !== songId)
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
    },
    createPlaylist(name) {
      this.playlists.push({ id: Date.now(), name, songs: [] })
      localStorage.setItem('playlists', JSON.stringify(this.playlists))
    }
  }
})
