# AI Interviewer - Frontend

React + TypeScript + Vite frontend for the AI Interviewer application.

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set VITE_API_URL if needed
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   ```
   http://localhost:5173
   ```

## Pages

### Admin Interface

- **Dashboard** (`/admin`) - List all interviews with filtering
- **Create Interview** (`/admin/create`) - Multi-step interview creation
- **Interview Details** (`/admin/interviews/:id`) - View details, match analysis, and reports

### Candidate Interface

- **Interview** (`/interview/:token`) - Chat-based interview interface

## Features

### Admin Features
- ✅ Create interviews with configuration
- ✅ Upload documents (resume, role description, job offering)
- ✅ View match analysis with AI scoring
- ✅ Generate candidate links
- ✅ View final reports with integrity flags
- ✅ Filter interviews by status

### Candidate Features
- ✅ Real-time chat interface
- ✅ Telemetry tracking (paste detection, response time)
- ✅ Progress indicator
- ✅ Completion screen

## Design System

### Colors
- Primary: Purple (`purple-500`)
- Secondary: Pink (`pink-500`)
- Background: Dark gradient (`slate-900` → `purple-900`)

### Components
- Glassmorphism: `bg-white/10 backdrop-blur-lg`
- Borders: `border border-white/20`
- Shadows: `shadow-2xl`
- Rounded corners: `rounded-2xl`

### Animations
- Smooth transitions: `transition-all duration-200`
- Loading spinners with bounce effects
- Progress bars with width transitions

## Build

```bash
npm run build
```

Output will be in `dist/` directory.

## Lint

```bash
npm run lint
```

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **TailwindCSS** - Styling
- **Fetch API** - HTTP client

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Project Structure

```
src/
├── api/
│   └── client.ts          # API client with TypeScript types
├── pages/
│   ├── AdminDashboard.tsx      # Interview list and stats
│   ├── CreateInterview.tsx     # Multi-step interview creation
│   ├── InterviewDetails.tsx    # Interview details and reports
│   └── CandidateInterview.tsx  # Chat interface for candidates
├── App.tsx                # Routing configuration
├── main.tsx              # Entry point
└── index.css             # Global styles
```

## Development

### Hot Module Replacement (HMR)
Vite provides fast HMR for instant feedback during development.

### Type Checking
TypeScript is configured for strict type checking. Run:
```bash
npm run type-check
```

### Code Formatting
Format code with Prettier (if configured):
```bash
npm run format
```

## Deployment

1. Build the production bundle:
   ```bash
   npm run build
   ```

2. Preview the build:
   ```bash
   npm run preview
   ```

3. Deploy the `dist/` directory to your hosting service.

## API Integration

The frontend communicates with the backend API through the `apiClient` in `src/api/client.ts`.

All API calls are typed with TypeScript interfaces for type safety.

## Troubleshooting

### CORS Errors
Ensure the backend has CORS configured for the frontend URL.

### API Connection Failed
Check that:
1. Backend server is running (`poetry run uvicorn app.main:app --reload`)
2. `VITE_API_URL` is set correctly in `.env`
3. No firewall blocking the connection

### Build Errors
Clear the cache and reinstall:
```bash
rm -rf node_modules dist
npm install
npm run build
```
