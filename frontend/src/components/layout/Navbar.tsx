import { Link } from 'react-router-dom';
import { Moon, Sun, LogOut, Settings, User, FileText } from 'lucide-react';
import { useThemeStore } from '@/store/theme.store';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';

export function Navbar() {
  const { theme, toggleTheme } = useThemeStore();
  const { user, logout } = useAuth();

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/dashboard" className="flex items-center gap-2 font-bold text-xl">
          <FileText className="h-6 w-6 text-primary" />
          <span>URCV</span>
        </Link>

        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>

          {user && (
            <>
              <Link to="/settings">
                <Button variant="ghost" size="icon" aria-label="Settings">
                  <Settings className="h-5 w-5" />
                </Button>
              </Link>

              <div className="flex items-center gap-2">
                <User className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium hidden md:inline">{user.full_name}</span>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => logout()}
                className="gap-2"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden md:inline">Logout</span>
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
