# Product Finder AI Agent - Frontend

A React chat interface for the Product Finder AI Agent. Users type natural language queries to search for products, and results are displayed as product cards within the conversation.

Built with React 19, TypeScript, and Vite.

## Prerequisites

- Node.js 18+

## Setup

Install dependencies:

```bash
npm install
```

## Running

Start the development server:

```bash
npm run dev
```

The app runs on `http://localhost:5173` and proxies `/chat` and `/health` requests to the backend at `http://localhost:8000`.

## Scripts

| Command           | Description                    |
| ----------------- | ------------------------------ |
| `npm run dev`     | Start dev server with HMR      |
| `npm run build`   | Compile TypeScript and bundle  |
| `npm run preview` | Preview production build       |
| `npm run lint`    | Run ESLint                     |
