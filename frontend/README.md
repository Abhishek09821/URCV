# URCV Frontend

Universal Resume Conversion & Verification - Frontend Application

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **React Router** - Navigation
- **Axios** - HTTP client
- **Framer Motion** - Animations
- **Lucide React** - Icons

## Features Implemented

### ✅ Authentication
- Login page with email/password
- Registration page with validation
- JWT token management with auto-refresh
- Protected routes
- Logout functionality

### ✅ Dashboard
- Resume statistics overview
- Recent resumes list
- Quick upload access
- Status badges (verified/pending)
- Confidence scores display

### ✅ Resume Upload
- Drag & drop file upload
- File validation (PDF, 10MB max)
- Upload progress
- Automatic parsing after upload
- Immediate navigation to resume details

### ✅ Resume Detail & Editor
- Complete resume data display
- Multi-section editor (Personal, Summary, Skills, etc.)
- Edit mode toggle
- Real-time updates
- Confidence score display
- Verification status

### ✅ ATS Analysis
- Overall ATS score display
- Category breakdown with progress bars
- Keywords found/missing
- Actionable improvement suggestions
- Priority-based recommendations
- Re-analyze functionality

### ✅ AI Improvements
- Section-based improvements
- Multiple improvement types (grammar, tone, etc.)
- Before/after comparison
- Apply/reject improvements
- User-controlled changes

### ✅ Export
- PDF export (ATS-optimized)
- DOCX support (coming soon)
- Export history tracking
- Download previous exports
- Format selection

### ✅ Settings
- Profile information display
- Password change
- Dark/light theme toggle
- Account status

### ✅ UI/UX Features
- Responsive mobile-first design
- Dark mode support
- Toast notifications
- Loading states
- Error handling
- Empty states
- Smooth animations
- Accessible components

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # Base UI components
│   │   ├── layout/       # Layout components
│   │   └── shared/       # Shared components
│   ├── features/
│   │   ├── auth/         # Authentication pages
│   │   ├── dashboard/    # Dashboard page
│   │   ├── resume/       # Resume pages & components
│   │   ├── ats/          # ATS analysis components
│   │   ├── export/       # Export page
│   │   └── settings/     # Settings page
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities & config
│   ├── services/         # API services
│   ├── store/            # Zustand stores
│   ├── styles/           # Global styles
│   ├── types/            # TypeScript types
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Building

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

### Linting

Run ESLint:
```bash
npm run lint
```

## API Integration

The frontend connects to the URCV backend API. Ensure the backend is running at the URL specified in `.env`.

### API Endpoints Used

- **Auth**: `/api/v1/auth/*`
- **Resumes**: `/api/v1/resumes/*`
- **ATS**: `/api/v1/resumes/{id}/analyze`
- **AI**: `/api/v1/resumes/{id}/improve`
- **Export**: `/api/v1/resumes/{id}/export`

## State Management

### Server State (TanStack Query)
- API data caching
- Automatic refetching
- Optimistic updates
- Loading/error states

### Client State (Zustand)
- Theme preferences
- Authentication state
- Current resume context

## Styling

### Tailwind CSS
- Utility-first approach
- Custom design tokens
- Dark mode support
- Responsive breakpoints

### CSS Variables
All colors defined as CSS variables in `styles/index.css` for easy theming.

## Type Safety

100% TypeScript coverage:
- All API types defined
- Form validation with Zod
- Props validation
- Hook types

## Performance

- Code splitting by route
- Lazy loading components
- Image optimization
- Debounced inputs
- Memoized expensive operations

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- Focus management

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Known Limitations

1. **Array Editing**: Education, Experience, Projects sections show placeholder for complex array editing
2. **DOCX Export**: Coming soon (PDF only for now)
3. **File Preview**: No PDF preview in browser (download only)
4. **Batch Operations**: No multi-resume selection/actions

## Future Enhancements

- [ ] Template marketplace
- [ ] Job description matching UI
- [ ] Resume comparison
- [ ] Collaborative editing
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Resume versioning
- [ ] Custom branding

## Deployment

### Vercel (Recommended)

1. Connect repository to Vercel
2. Set environment variables
3. Deploy

### Docker

```bash
docker build -t urcv-frontend .
docker run -p 3000:3000 urcv-frontend
```

### Static Hosting

Build and upload `dist/` folder to any static host:
- Netlify
- Cloudflare Pages
- AWS S3 + CloudFront
- GitHub Pages

## Contributing

1. Follow existing code style
2. Write TypeScript (no `any` types)
3. Add proper error handling
4. Test responsiveness
5. Check accessibility

## License

MIT License - See LICENSE file

## Support

For issues or questions, contact the development team.

---

**URCV Frontend - Built with ❤️ using React + TypeScript**
