import React, { useEffect, useState } from 'react'

type Article = {
  id: string
  title: string
  url: string
  scraped_at: string
}

type LatestResponse = {
  updated_at: string | null
  count: number
  items: Article[]
}

type User = {
  id: number | string
  name?: string
  login?: string
  avatar_url?: string
}

const API_BASE = 'http://localhost:8000'

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null)
  const [latest, setLatest] = useState<LatestResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadMe = async () => {
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        credentials: 'include',
      })
      if (!res.ok) {
        setUser(null)
        return
      }
      const data = await res.json()
      setUser(data)
    } catch (err: any) {
      setError(err.message ?? 'Failed to load user')
    }
  }

  const loadLatest = async () => {
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/data`, {
        credentials: 'include',
      })
      if (!res.ok) {
        throw new Error(`Failed to load data (${res.status})`)
      }
      const data = (await res.json()) as LatestResponse
      setLatest(data)
    } catch (err: any) {
      setError(err.message ?? 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const scrapeNow = async () => {
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/scrape`, {
        credentials: 'include',
      })
      if (!res.ok) {
        throw new Error(`Scrape failed (${res.status})`)
      }
      const data = await res.json()
      setLatest({
        updated_at: data.items?.[0]?.scraped_at ?? null,
        count: data.count ?? data.items?.length ?? 0,
        items: data.items ?? [],
      })
    } catch (err: any) {
      setError(err.message ?? 'Failed to scrape')
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    setError(null)
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
      setUser(null)
      setLatest(null)
    } catch (err: any) {
      setError(err.message ?? 'Failed to logout')
    }
  }

  useEffect(() => {
    loadMe()
  }, [])

  const loginUrl = `${API_BASE}/auth/login`

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Restaverse Real-Time Scraper</h1>
        {user ? (
          <div className="user-info">
            {user.avatar_url && (
              <img src={user.avatar_url} alt={user.name ?? user.login} className="avatar" />
            )}
            <div>
              <div className="user-name">{user.name ?? user.login}</div>
              <button className="btn-secondary" onClick={logout}>
                Logout
              </button>
            </div>
          </div>
        ) : (
          <a href={loginUrl} className="btn-primary">
            Login with OAuth
          </a>
        )}
      </header>

      <main className="app-main">
        {!user ? (
          <section className="card centered">
            <h2>Sign in to start scraping</h2>
            <p>
              This demo uses OAuth (GitHub example) and a lightweight cookie-based session so only
              authenticated users can trigger scraping and view the data.
            </p>
            <a href={loginUrl} className="btn-primary">
              Login with OAuth
            </a>
          </section>
        ) : (
          <>
            <section className="card controls">
              <h2>Scraping Controls</h2>
              <p>
                Click <strong>Fetch Latest Now</strong> to trigger a real-time scrape of the Hacker
                News front page. A background cron job also refreshes the data roughly every hour.
              </p>
              <div className="buttons">
                <button className="btn-primary" onClick={scrapeNow} disabled={loading}>
                  {loading ? 'Fetching…' : 'Fetch Latest Now'}
                </button>
                <button className="btn-secondary" onClick={loadLatest} disabled={loading}>
                  Refresh from Cache
                </button>
              </div>
              {latest?.updated_at && (
                <p className="meta">
                  Last updated: <span>{new Date(latest.updated_at).toLocaleString()}</span> —{' '}
                  {latest.count} articles
                </p>
              )}
            </section>

            <section className="card">
              <h2>Scraped Articles</h2>
              {error && <div className="alert error">{error}</div>}
              {!latest || latest.count === 0 ? (
                <p>No data yet. Run a scrape to see results.</p>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Title</th>
                        <th>Link</th>
                        <th>Scraped At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {latest.items.slice(0, 50).map((item, index) => (
                        <tr key={item.id ?? index}>
                          <td>{index + 1}</td>
                          <td>{item.title}</td>
                          <td>
                            <a href={item.url} target="_blank" rel="noreferrer">
                              Open
                            </a>
                          </td>
                          <td>{new Date(item.scraped_at).toLocaleTimeString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </main>

      <footer className="app-footer">
        <span>Restaverse · FastAPI + React · OAuth + Real-time scraping</span>
      </footer>
    </div>
  )
}


