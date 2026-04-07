<template>
  <canvas ref="canvas" class="animated-bg"></canvas>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'AnimatedBackground',
  setup() {
    const canvas = ref(null)
    let animationId = null
    let time = 0

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    const DOT_SPACING = 40
    const DOT_RADIUS = 1.5
    const LINE_DISTANCE = 80
    const DOT_COLOR = { r: 59, g: 130, b: 246 }

    function draw(ctx, width, height) {
      ctx.clearRect(0, 0, width, height)
      time += 0.015

      const cols = Math.ceil(width / DOT_SPACING) + 1
      const rows = Math.ceil(height / DOT_SPACING) + 1
      const dots = []

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = i * DOT_SPACING
          const y = j * DOT_SPACING
          const wave = Math.sin(time + i * 0.15 + j * 0.15) * 0.5 + 0.5
          const alpha = 0.03 + wave * 0.05
          const scale = 0.8 + wave * 0.4

          ctx.beginPath()
          ctx.arc(x, y, DOT_RADIUS * scale, 0, Math.PI * 2)
          ctx.fillStyle = `rgba(${DOT_COLOR.r}, ${DOT_COLOR.g}, ${DOT_COLOR.b}, ${alpha})`
          ctx.fill()

          dots.push({ x, y, alpha })
        }
      }

      // Draw constellation lines between nearby dots
      ctx.lineWidth = 0.5
      for (let i = 0; i < dots.length; i++) {
        for (let j = i + 1; j < dots.length; j++) {
          const dx = dots[i].x - dots[j].x
          const dy = dots[i].y - dots[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < LINE_DISTANCE && dist > DOT_SPACING * 0.5) {
            const lineAlpha = (1 - dist / LINE_DISTANCE) * 0.03 * (dots[i].alpha + dots[j].alpha)
            ctx.beginPath()
            ctx.moveTo(dots[i].x, dots[i].y)
            ctx.lineTo(dots[j].x, dots[j].y)
            ctx.strokeStyle = `rgba(${DOT_COLOR.r}, ${DOT_COLOR.g}, ${DOT_COLOR.b}, ${lineAlpha})`
            ctx.stroke()
          }
        }
      }
    }

    function animate() {
      const c = canvas.value
      if (!c) return
      const ctx = c.getContext('2d')
      draw(ctx, c.width, c.height)
      animationId = requestAnimationFrame(animate)
    }

    function resize() {
      const c = canvas.value
      if (!c) return
      const dpr = window.devicePixelRatio || 1
      const rect = c.parentElement.getBoundingClientRect()
      c.width = rect.width * dpr
      c.height = rect.height * dpr
      c.style.width = rect.width + 'px'
      c.style.height = rect.height + 'px'
      const ctx = c.getContext('2d')
      ctx.scale(dpr, dpr)
    }

    function handleVisibility() {
      if (document.hidden) {
        if (animationId) cancelAnimationFrame(animationId)
        animationId = null
      } else {
        if (!animationId) animate()
      }
    }

    onMounted(() => {
      if (prefersReducedMotion) return
      resize()
      animate()
      window.addEventListener('resize', resize)
      document.addEventListener('visibilitychange', handleVisibility)
    })

    onBeforeUnmount(() => {
      if (animationId) cancelAnimationFrame(animationId)
      window.removeEventListener('resize', resize)
      document.removeEventListener('visibilitychange', handleVisibility)
    })

    return { canvas }
  }
}
</script>

<style scoped>
.animated-bg {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: var(--sidebar-width, 240px);
  z-index: 0;
  pointer-events: none;
}
</style>
