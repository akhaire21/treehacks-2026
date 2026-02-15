'use client'

import { GrainGradient } from '@paper-design/shaders-react'

export default function Background() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: -1 }}>
      <GrainGradient
        style={{ width: '100%', height: '100%' }}
        colors={["#42ae5f", "#2c9031", "#3eb036", "#319b5d"]}
        colorBack="#000000"
        softness={0.5}
        intensity={0.5}
        noise={0.25}
        shape="corners"
        speed={1}
      />
    </div>
  )
}
