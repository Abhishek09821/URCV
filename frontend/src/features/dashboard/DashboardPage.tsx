import { Link } from 'react-router-dom';
import { useResumes } from '@/hooks/useResumes';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Badge } from '@/components/ui/Badge';
import { FileText, Upload, CheckCircle, AlertCircle, TrendingUp, Clock } from 'lucide-react';
import { formatDate, getScoreBadgeColor } from '@/lib/utils';

export function DashboardPage() {
  const { resumes, total, isLoading } = useResumes();

  const verified = resumes.filter((r) => r.is_verified).length;
  const avgConfidence =
    resumes.length > 0
      ? Math.round(resumes.reduce((acc, r) => acc + r.confidence_score, 0) / resumes.length)
      : 0;

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Manage your resumes and track progress</p>
          </div>
          <Link to="/upload">
            <Button className="gap-2">
              <Upload className="h-4 w-4" />
              Upload Resume
            </Button>
          </Link>
        </div>

        {/* Stats */}
        {!isLoading && (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Resumes</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{total}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Verified</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{verified}</div>
                <p className="text-xs text-muted-foreground">
                  {total > 0 ? Math.round((verified / total) * 100) : 0}% of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{avgConfidence}%</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Need Review</CardTitle>
                <AlertCircle className="h-4 w-4 text-yellow-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{total - verified}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Resumes List */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Resumes</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="py-12">
                <LoadingSpinner size="lg" />
              </div>
            ) : resumes.length === 0 ? (
              <EmptyState
                icon={<FileText className="h-12 w-12 text-muted-foreground" />}
                title="No resumes yet"
                description="Upload your first resume to get started with URCV"
                action={
                  <Link to="/upload">
                    <Button className="gap-2">
                      <Upload className="h-4 w-4" />
                      Upload Resume
                    </Button>
                  </Link>
                }
              />
            ) : (
              <div className="space-y-4">
                {resumes.map((resume) => (
                  <Link
                    key={resume.id}
                    to={`/resume/${resume.id}`}
                    className="block rounded-lg border p-4 transition-colors hover:bg-accent"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                          <FileText className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h3 className="font-medium">
                            {resume.resume_data.personal?.full_name || resume.original_filename}
                          </h3>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            <span>{formatDate(resume.created_at)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {resume.is_verified ? (
                          <Badge variant="success" className="gap-1">
                            <CheckCircle className="h-3 w-3" />
                            Verified
                          </Badge>
                        ) : (
                          <Badge variant="warning" className="gap-1">
                            <AlertCircle className="h-3 w-3" />
                            Review
                          </Badge>
                        )}
                        <Badge className={getScoreBadgeColor(resume.confidence_score)}>
                          {resume.confidence_score}% Confidence
                        </Badge>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
