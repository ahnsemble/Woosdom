import { AppContextProvider } from './contexts/AppContext.tsx'
import AppLayout from './components/AppLayout.tsx'

export default function App() {
  return (
    <AppContextProvider>
      <AppLayout />
    </AppContextProvider>
  )
}
