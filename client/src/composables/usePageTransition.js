import { ref } from 'vue'
import { useRouter } from 'vue-router'

const ROUTE_INDEX = {
  '/': 0,
  '/inventory': 1,
  '/orders': 2,
  '/spending': 3,
  '/demand': 4,
  '/reports': 5
}

export function usePageTransition() {
  const transitionName = ref('slide-left')
  const router = useRouter()

  router.beforeEach((to, from) => {
    const toIndex = ROUTE_INDEX[to.path] ?? 0
    const fromIndex = ROUTE_INDEX[from.path] ?? 0
    transitionName.value = toIndex >= fromIndex ? 'slide-left' : 'slide-right'
  })

  return { transitionName }
}
