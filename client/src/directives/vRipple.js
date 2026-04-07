import gsap from 'gsap'

export const vRipple = {
  mounted(el) {
    el.style.position = 'relative'
    el.style.overflow = 'hidden'

    el.__rippleHandler = (e) => {
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const size = Math.max(rect.width, rect.height) * 2

      const ripple = document.createElement('span')
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.35);
        width: ${size}px;
        height: ${size}px;
        left: ${x - size / 2}px;
        top: ${y - size / 2}px;
        pointer-events: none;
        transform: scale(0);
      `
      el.appendChild(ripple)

      gsap.to(ripple, {
        scale: 1,
        opacity: 0,
        duration: 0.6,
        ease: 'power2.out',
        onComplete: () => ripple.remove()
      })
    }

    el.addEventListener('click', el.__rippleHandler)
  },

  unmounted(el) {
    if (el.__rippleHandler) {
      el.removeEventListener('click', el.__rippleHandler)
    }
  }
}
