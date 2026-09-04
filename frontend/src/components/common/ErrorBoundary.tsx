import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: (error: Error) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback && this.state.error) {
        return this.props.fallback(this.state.error);
      }
      return (
        <div className="p-4 m-4 bg-error/10 text-error border border-error rounded">
          <h2 className="font-bold mb-2">Something went wrong.</h2>
          <p className="text-sm font-mono whitespace-pre-wrap">{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
