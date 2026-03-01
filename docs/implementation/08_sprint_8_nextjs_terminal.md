# Sprint 8 Implementation: The Next.js Command Terminal

## The Objective
In Sprints 1-7, the fundamental quantitative systems and automated execution engines were built. The UI during Phase 1-4 was strictly a read-only Grafana dashboard.

Sprint 8 initiates Phase 5 of the Roadmap. We now build the bespoke `STOCKSTATS` Next.js frontend application. This is not a public SaaS; it is a proprietary, hyper-secure internal Command Center for visualizing our algorithmic state and managing the `ShadowExecutionEngine`.

**Reference:** [Strategy 07 (Frontend Architecture)](../strategy/07_frontend_and_navigation.md)

---

## Step 1: Frontend Repository Scaffolding

We must stand up the React 18, Next.js 14, and Tailwind ecosystem.

**1.1 Scaffolding (`/frontend`):**
Navigate to the root directory in the terminal.
```bash
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"
```
*   Select `Yes` to use the App Router.

**1.2 Component Library:**
We utilize `shadcn/ui` for rapid, accessible, and heavily customizable UI primitives (buttons, modals, tables) without the bloat of traditional component libraries.
```bash
cd frontend
npx shadcn-ui@latest init
# Accept the defaults (New York style, Zinc neutral color)
```

## Step 3: Role-Based Access Control (RBAC) Architecture

As defined in Strategy 07, the UI physically alters itself based on the JSON Web Token (JWT) of the user signing in.

**3.1 Implement Route Middleware (`frontend/src/middleware.ts`):**
Next.js Edge Middleware allows us to mathematically intercept a page request before the server renders it, physically blocking a `Viewer` from loading the `Trader` manual execution routes.

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtDecode } from "jwt-decode"; // Requires: npm i jwt-decode

export function middleware(request: NextRequest) {
  const token = request.cookies.get('stockstats_auth_token')?.value
  
  // 1. Unauthenticated -> Redirect to Login
  if (!token && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (token) {
    try {
      const decoded: any = jwtDecode(token);
      const userRole: string = decoded.role; // e.g., 'ADMIN', 'TRADER', 'VIEWER'
      const path = request.nextUrl.pathname;
      
      // 2. Viewer trying to access a secure route (e.g., placing manual trades)
      if (userRole === 'VIEWER' && path.startsWith('/execution')) {
        // Render the exact same 404 page that a missing route would render.
        // This is a military-grade security posture: We don't say "Unauthorized".
        // We say "This page does not exist."
        return NextResponse.rewrite(new URL('/404', request.url))
      }
      
      // 3. Analyst trying to access Admin Configuration
      if (userRole !== 'ADMIN' && path.startsWith('/admin')) {
         return NextResponse.rewrite(new URL('/404', request.url))
      }
      
    } catch (error) {
       // Corrupted Token
       return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

## Step 4: Time-Series State Management

To render the live L1 ticks and the GARCH bands seamlessly bridging the Python backend and the React frontend, we must connect Next.js directly to the Redis Pub/Sub streams using Server-Sent Events (SSE) or WebSockets.

**4.1 Implement SWR / React Query:**
We do not use standard `useEffect` hooks to poll TimescaleDB. We must use `SWR` (Stale-While-Revalidate) to map our React Component state directly to the active REST API.

```bash
npm install swr
```
```tsx
// frontend/src/components/ChartWidget.tsx
'use client'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function ChartWidget({ symbol }: { symbol: string }) {
  // 1. Fetch the massive historical 5-minute VWAP array from the Node.js API
  const { data, error, isLoading } = useSWR(`/api/timeseries/${symbol}`, fetcher, {
      refreshInterval: 1000 // Poll lightweight API every 1s 
  })

  if (isLoading) return <div>Loading High-Frequency Matrix...</div>
  if (error) return <div>Data Engine Disconnected. Veto Active.</div>

  // 2. Render utilizing a library like Lightweight Charts
  return (
    <div className="border border-zinc-800 rounded bg-black p-4">
      <h3 className="text-zinc-300 font-mono">{symbol} L1 Tape</h3>
      {/* <LightweightChart data={data} /> */}
    </div>
  )
}
```

---
**Sprint 8 Complete.** 
The proprietary Front-End architecture is now scaffolded. It utilizes Next.js App Router, intercepts unauthorized access via Edge Middleware, and fetches time-series data asynchronously.

Proceed to **Sprint 9: State Reconciliation** to build the database verification loops required to prevent "Zombie Orders" on the exchange.
