import { useEffect, useState } from 'react'
import Authentication from './Components/Authentication'
import TaskCreator from './Components/TaskCreator'

function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    async function fetchUser() {
      try {
        const res = await fetch('/.auth/me') // <-- fixed
        if (!res.ok) throw new Error('Failed to fetch user')
        const data = await res.json()
        setUser(data.clientPrincipal)
      } catch (err) {
        console.error(err)
      }
    }
    fetchUser()
  }, [])

  if (user) {
    return <div>
      <TaskCreter/>
    </div>
  } else {
    return <Authentication />
  }
}

export default App
