## Frontend Setup

### Prerequisites
- Node.js 20+
- npm 10+
- Angular CLI 17+

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Install Angular CLI globally (if not already):
```bash
npm install -g @angular/cli
```

### Development Server

Start development server:
```bash
npm start
```

Navigate to `http://localhost:4200/`. The app will automatically reload on file changes.

### Build

Build for production:
```bash
npm run build:prod
```

Output will be in `dist/frontend/` directory.

### Project Structure

```
src/
├── app/
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── services/          # HTTP services
│   ├── guards/            # Route guards
│   ├── models/            # Interfaces
│   ├── app.component.ts   # Root component
│   ├── app.routes.ts      # Route definitions
│   └── app.config.ts      # App configuration
├── assets/                # Static assets
├── styles.scss            # Global styles
├── index.html             # HTML entry point
└── main.ts                # Bootstrap
```

### Features

1. **Authentication**
   - User registration and login
   - JWT token-based authentication
   - Protected routes with guards

2. **Dashboard**
   - Statistics overview
   - Quick action buttons
   - Navigation menu

3. **Detection Interface**
   - Real-time image detection
   - Upload and analyze images
   - Display detection results

4. **Product Management**
   - List all products
   - Filter by brand
   - Add/edit/delete products

5. **Training Management**
   - Start training sessions
   - Monitor training progress
   - View model metrics

### Styling

- SCSS for component styles
- Global styles in `styles.scss`
- Responsive design with media queries
- Flexbox and CSS Grid layouts

### HTTP Interceptor

Auth interceptor automatically attaches JWT token to all API requests:
- Intercepts all HTTP requests
- Adds Authorization header with Bearer token
- Handles token management

### Environment Configuration

Update API URL in services if needed:
- `auth.service.ts` - Authentication API
- `product.service.ts` - Product API
- `detection.service.ts` - Detection API
- `training.service.ts` - Training API
