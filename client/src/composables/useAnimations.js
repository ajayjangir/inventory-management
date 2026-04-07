import gsap from 'gsap'

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function useAnimations() {
  const timelines = []

  function track(tl) {
    timelines.push(tl)
    return tl
  }

  function staggerFadeUp(selector, options = {}) {
    if (prefersReducedMotion) return null
    const els = document.querySelectorAll(selector)
    if (!els.length) return null
    const tl = gsap.from(els, {
      opacity: 0,
      y: 30,
      duration: options.duration || 0.5,
      stagger: options.stagger || 0.08,
      ease: options.ease || 'power3.out',
      delay: options.delay || 0
    })
    return track(tl)
  }

  function countUp(el, endValue, options = {}) {
    if (prefersReducedMotion) {
      if (el && options.formatter) el.textContent = options.formatter(endValue)
      return null
    }
    const obj = { value: 0 }
    const tl = gsap.to(obj, {
      value: endValue,
      duration: options.duration || 1.5,
      ease: options.ease || 'power2.out',
      delay: options.delay || 0,
      onUpdate: () => {
        if (el) {
          el.textContent = options.formatter
            ? options.formatter(obj.value)
            : Math.round(obj.value).toLocaleString()
        }
      }
    })
    return track(tl)
  }

  function barGrow(selector, options = {}) {
    if (prefersReducedMotion) return null
    const els = document.querySelectorAll(selector)
    if (!els.length) return null
    const tl = gsap.from(els, {
      width: 0,
      duration: options.duration || 1,
      stagger: options.stagger || 0.1,
      ease: options.ease || 'elastic.out(1, 0.5)',
      delay: options.delay || 0
    })
    return track(tl)
  }

  function springPop(selector, options = {}) {
    if (prefersReducedMotion) return null
    const els = typeof selector === 'string' ? document.querySelectorAll(selector) : [selector]
    if (!els.length) return null
    const tl = gsap.from(els, {
      scale: 0.85,
      opacity: 0,
      duration: options.duration || 0.5,
      stagger: options.stagger || 0.06,
      ease: 'back.out(1.7)',
      delay: options.delay || 0
    })
    return track(tl)
  }

  function staggerTableRows(selector, options = {}) {
    if (prefersReducedMotion) return null
    const rows = document.querySelectorAll(`${selector} tbody tr`)
    if (!rows.length) return null
    const maxRows = options.maxRows || 15
    const visible = Array.from(rows).slice(0, maxRows)
    const tl = gsap.from(visible, {
      opacity: 0,
      x: -20,
      duration: options.duration || 0.4,
      stagger: options.stagger || 0.03,
      ease: 'power2.out',
      delay: options.delay || 0
    })
    return track(tl)
  }

  function animateDonut(selector, options = {}) {
    if (prefersReducedMotion) return null
    const circles = document.querySelectorAll(`${selector} circle[stroke-dasharray]`)
    if (!circles.length) return null
    const tl = gsap.timeline({ delay: options.delay || 0 })
    circles.forEach((circle, i) => {
      const target = circle.getAttribute('stroke-dasharray')
      circle.setAttribute('stroke-dasharray', '0 408')
      tl.to(circle, {
        attr: { 'stroke-dasharray': target },
        duration: 0.8,
        ease: 'power3.out'
      }, i * 0.15)
    })
    return track(tl)
  }

  function cleanup() {
    timelines.forEach(tl => {
      if (tl && tl.kill) tl.kill()
    })
    timelines.length = 0
  }

  return {
    staggerFadeUp,
    countUp,
    barGrow,
    springPop,
    staggerTableRows,
    animateDonut,
    cleanup
  }
}
