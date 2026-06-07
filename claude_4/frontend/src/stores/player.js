import { defineStore } from 'pinia'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    currentSong: null,
    isPlaying: false,
    playlist: [],
    currentIndex: 0,
    volume: 0.8,
    progress: 0,
    duration: 0
  }),
  actions: {
    play(song) {
      this.currentSong = song
      this.isPlaying = true
    },
    togglePlay() {
      this.isPlaying = !this.isPlaying
    },
    setPlaylist(songs, index = 0) {
      this.playlist = songs
      this.currentIndex = index
    }
  }
})
