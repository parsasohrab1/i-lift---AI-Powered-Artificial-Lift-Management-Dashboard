# IntelliLift Frontend

Frontend application built with Next.js 14, React, and TypeScript.

## Features

- ✅ Next.js 14 with App Router
- ✅ TypeScript
- ✅ Tailwind CSS
- ✅ React Query for data fetching
- ✅ Authentication with JWT
- ✅ Real-time data updates
- ✅ Responsive design
- ✅ Charts and visualizations (Recharts)

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── dashboard/    # Dashboard pages
│   │   ├── login/        # Login page
│   │   └── layout.tsx    # Root layout
│   ├── components/       # React components
│   │   ├── auth/         # Authentication components
│   │   ├── dashboard/    # Dashboard components
│   │   ├── layouts/      # Layout components
│   │   ├── sensors/      # Sensor components
│   │   └── ui/           # UI components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities
│   └── types/            # TypeScript types
└── public/               # Static files
```

## Pages

- `/` - Home (redirects to dashboard)
- `/login` - Login page
- `/dashboard` - Main dashboard
- `/dashboard/sensors` - Sensor data
- `/dashboard/wells` - Wells management
- `/dashboard/analytics` - Analytics
- `/dashboard/ml` - ML predictions
- `/dashboard/alerts` - Alerts
- `/dashboard/settings` - Settings

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Authentication

The app uses JWT tokens stored in localStorage. Tokens are automatically refreshed when they expire.

## State Management

- React Query for server state
- Local state with useState/useReducer
- Auth context for user state

## Styling

- Tailwind CSS for styling
- Custom color scheme with primary colors
- Responsive design with mobile-first approach

## API Integration

All API calls go through `src/lib/api.ts` which includes:
- Automatic token injection
- Token refresh on 401
- Error handling
- Request/response interceptors

