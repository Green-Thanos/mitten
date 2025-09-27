"use client"

import { useState, useEffect } from "react"

export default function Globe() {
  const [showHint, setShowHint] = useState(true)

  useEffect(() => {
    const hintTimer = setTimeout(() => {
      setShowHint(false)
    }, 3000)

    return () => clearTimeout(hintTimer)
  }, [])

  return (
    <div className="fixed top-0 left-0 w-full h-full z-0 flex items-center justify-center">
      {/* Starfield Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="stars"></div>
        <div className="stars2"></div>
        <div className="stars3"></div>
      </div>

      {/* Globe Container */}
      <div className="relative">
        {/* Outer Glow */}
        <div className="absolute inset-0 rounded-full bg-gradient-radial from-blue-400/20 via-purple-500/10 to-transparent blur-xl scale-150 animate-pulse-slow"></div>

        {/* Main Globe */}
        <div className="relative w-80 h-80 rounded-full bg-gradient-conic from-blue-500 via-purple-500 via-pink-500 via-orange-500 to-blue-500 animate-spin-slow shadow-2xl">
          {/* Inner Globe */}
          <div className="absolute inset-2 rounded-full bg-gradient-radial from-blue-900/80 via-purple-900/60 to-black/40 backdrop-blur-sm">
            {/* Wireframe Effect */}
            <div className="absolute inset-0 rounded-full border-2 border-blue-400/30 animate-pulse"></div>
            <div className="absolute inset-4 rounded-full border border-purple-400/20 animate-pulse-reverse"></div>
            <div className="absolute inset-8 rounded-full border border-pink-400/15 animate-pulse"></div>

            {/* Grid Lines */}
            <div className="absolute inset-0 rounded-full overflow-hidden">
              <div className="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-400/30 to-transparent"></div>
              <div className="absolute top-1/3 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-400/20 to-transparent"></div>
              <div className="absolute top-2/3 left-0 right-0 h-px bg-gradient-to-r from-transparent via-pink-400/20 to-transparent"></div>
              <div className="absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-transparent via-blue-400/30 to-transparent"></div>
              <div className="absolute top-0 bottom-0 left-1/3 w-px bg-gradient-to-b from-transparent via-purple-400/20 to-transparent"></div>
              <div className="absolute top-0 bottom-0 left-2/3 w-px bg-gradient-to-b from-transparent via-pink-400/20 to-transparent"></div>
            </div>

            {/* Floating Particles */}
            <div className="absolute inset-0 rounded-full overflow-hidden">
              <div className="particle particle-1"></div>
              <div className="particle particle-2"></div>
              <div className="particle particle-3"></div>
              <div className="particle particle-4"></div>
              <div className="particle particle-5"></div>
            </div>
          </div>
        </div>

        {/* Orbital Rings */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-96 h-96 border border-blue-400/20 rounded-full animate-spin-reverse-slow"></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-[28rem] h-[28rem] border border-purple-400/15 rounded-full animate-spin-slow transform rotate-45"></div>
        </div>
      </div>

      {/* Interaction Hint */}
      {showHint && (
        <div className="absolute bottom-4 right-4 bg-black/30 backdrop-blur-sm text-white text-sm px-3 py-1 rounded-full transition-opacity duration-1000 opacity-80 hover:opacity-100 border border-white/10">
          Explore The Orb
        </div>
      )}
    </div>
  )
}
