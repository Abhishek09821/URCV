import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useExportResume, useExportHistory } from '@/hooks/useExport';
import { useResume } from '@/hooks/useResumes';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorMessage } from '@/components/shared/ErrorMessage';
import { ArrowLeft, FileDown, Clock, Download } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';
import type { ExportRequest } from '@/types';

export function ExportPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { resume, isLoading: resumeLoading } = useResume(id);
  const { data: history, isLoading: historyLoading } = useExportHistory(id!);
  const exportMutation = useExportResume(id!);
  
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx'>('pdf');

  const handleExport = () => {
    const request: ExportRequest = {
      format: selectedFormat,
    };
    exportMutation.mutate(request);
  };

  if (resumeLoading) {
    return (
      <AppLayout>
        <div className="flex h-96 items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  if (!resume) {
    return (
      <AppLayout>
        <ErrorMessage message="Resume not found" />
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/resume/${id}`)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Export Resume</h1>
            <p className="text-sm text-muted-foreground">
              {resume.resume_data.personal?.full_name || 'Your Resume'}
            </p>
          </div>
        </div>

        {/* Export Options */}
        <Card>
          <CardHeader>
            <CardTitle>Export Format</CardTitle>
            <CardDescription>Choose the format for your exported resume</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Format Selection */}
            <div className="grid gap-4 md:grid-cols-2">
              <button
                type="button"
                onClick={() => setSelectedFormat('pdf')}
                className={`rounded-lg border-2 p-6 text-left transition-colors ${
                  selectedFormat === 'pdf'
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-semibold">PDF (ATS-Optimized)</h3>
                  <Badge variant="success">Recommended</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  Single column, standard fonts, ATS-friendly formatting
                </p>
              </button>

              <button
                type="button"
                onClick={() => setSelectedFormat('docx')}
                className={`rounded-lg border-2 p-6 text-left transition-colors ${
                  selectedFormat === 'docx'
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-semibold">DOCX (Word)</h3>
                  <Badge variant="info">Coming Soon</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  Editable Word document format
                </p>
              </button>
            </div>

            {/* ATS Info */}
            <div className="rounded-lg bg-blue-50 p-4 text-sm dark:bg-blue-950">
              <h4 className="mb-2 font-medium text-blue-900 dark:text-blue-100">
                ATS-Optimized Export
              </h4>
              <ul className="space-y-1 text-blue-800 dark:text-blue-200">
                <li>✓ Single column layout for better parsing</li>
                <li>✓ Standard fonts (Arial, Times New Roman)</li>
                <li>✓ Clear section headings</li>
                <li>✓ No images, tables, or complex formatting</li>
                <li>✓ Bullet points preserved</li>
              </ul>
            </div>

            {/* Export Button */}
            <Button
              onClick={handleExport}
              isLoading={exportMutation.isPending}
              disabled={selectedFormat === 'docx'}
              className="w-full gap-2"
              size="lg"
            >
              <FileDown className="h-5 w-5" />
              Export as {selectedFormat.toUpperCase()}
            </Button>
          </CardContent>
        </Card>

        {/* Export History */}
        <Card>
          <CardHeader>
            <CardTitle>Export History</CardTitle>
            <CardDescription>Your previous exports</CardDescription>
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <div className="py-8">
                <LoadingSpinner />
              </div>
            ) : !history || history.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                No exports yet. Export your resume to see history here.
              </p>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between rounded-lg border p-4"
                  >
                    <div className="flex items-center gap-3">
                      <FileDown className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{item.format.toUpperCase()} Export</p>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>{formatDateTime(item.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(item.file_url, '_blank')}
                      className="gap-2"
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
