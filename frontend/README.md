# UberEats Clone - Frontend

This is the frontend application for the UberEats Clone, built with modern web technologies to ensure a scalable, maintainable, and high-performance user interface.

## Technologies Used

- **Framework**: [React 19](https://react.dev/)
- **Bundler**: [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Routing**: [React Router v7](https://reactrouter.com/)
- **API Client**: [Axios](https://axios-http.com/)

---

## Getting Started

### Prerequisites

Ensure you have the following installed:

- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- `npm` (comes with Node.js)

### Installation

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Set up environment variables:
   Ensure the `VITE_API_URL` points to your local backend server (e.g., `http://localhost:8000/api`).

### Running the Application

To start the development server with Hot Module Replacement (HMR):

```bash
npm run dev
```

To build the application for production:

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

---

## Architecture & Folder Structure

This project follows a **Feature-Sliced Design** to ensure scalability as the application grows.

```text
src/
├── api/             # Global Axios configuration and interceptors
├── assets/          # Static files (images, SVGs, custom fonts)
├── components/      # Global, reusable UI components (Buttons, Inputs, Layouts)
├── context/         # Global React Contexts (e.g., AuthContext)
├── features/        # Feature-based modules (Core of the app's business logic)
│   ├── auth/        # Auth logic, services, and types
│   ├── restaurants/ # Restaurant-related logic
│   ├── cart/        # Cart and checkout logic
│   └── orders/      # Order history and tracking
├── hooks/           # Global custom hooks (e.g., useAuth)
├── layouts/         # Page layout wrappers (MainLayout, AuthLayout)
├── pages/           # High-level route entry points
├── routes/          # Application routing configuration
├── types/           # Shared global TypeScript definitions
└── utils/           # Helper functions (formatters, parsers)
```

---

## Development Best Practices

### 1. Feature Separation

Do not dump all components into `src/components`. If a component, type, or service is specific to a feature (e.g., `RestaurantCard`), it should live inside its respective folder in `src/features/`.

### 2. API Calls

All HTTP requests should route through `src/api/client.ts`. Feature-specific API requests should be defined in their own service files (e.g., `src/features/auth/services/auth.service.ts`).

### 3. State Management

Authentication state is managed via React Context (`AuthContext`). Avoid introducing heavy state management libraries like Redux unless there is a strongly justified architectural need.

### 4. Styling

Use Tailwind utility classes directly in your JSX. Avoid writing custom CSS files unless absolutely necessary (e.g., complex keyframe animations).
