import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useResume, useVerifyResume, useDeleteResume } from '@/hooks/useResumes';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorMessage } from '@/components/shared/ErrorMessage';
import { ResumeEditor } from './components/ResumeEditor';
import { ATSAnalysisCard } from '../ats/components/ATSAnalysisCard';
import { AIImprovementCard } from '../ats/components/AIImprovementCard';
import {
  CheckCircle,
  AlertCircle,
  Edit2,
  FileDown,
  Trash2,
  ArrowLeft,
  Sparkles,
  BarChart3,
} from 'lucide-react';
import { formatDate } from '@/lib/utils';

export function ResumeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { resume, isLoading, error } = useResume(id);
  const verifyMutation = useVerifyResume(id!);
  const deleteMutation = useDeleteResume();
  const [isEditing, setIsEditing] = useState(false);
  const [showATS, setShowATS] = useState(false);
  const [showAI, setShowAI] = useState(false);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex h-96 items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  if (error || !resume) {
    return (
      <AppLayout>
        <ErrorMessage message="Failed to load resume" />
      </AppLayout>
    );
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this resume?')) {
      deleteMutation.mutate(resume.id, {
        onSuccess: () => navigate('/dashboard'),
      });
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold">
                {resume.resume_data.personal?.full_name || 'Resume Details'}
              </h1>
              <p className="text-sm text-muted-foreground">
                Uploaded {formatDate(resume.created_at)}
              </p>
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
                Not Verified
              </Badge>
            )}
            <Badge>{resume.confidence_score}% Confidence</Badge>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={isEditing ? 'secondary' : 'default'}
            className="gap-2"
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit2 className="h-4 w-4" />
            {isEditing ? 'View Mode' : 'Edit Resume'}
          </Button>

          <Button
            variant="outline"
            className="gap-2"
            onClick={() => setShowATS(!showATS)}
          >
            <BarChart3 className="h-4 w-4" />
            {showATS ? 'Hide' : 'Show'} ATS Analysis
          </Button>

          <Button
            variant="outline"
            className="gap-2"
            onClick={() => setShowAI(!showAI)}
          >
            <Sparkles className="h-4 w-4" />
            AI Improvements
          </Button>

          <Button
            variant="outline"
            className="gap-2"
            onClick={() => navigate(`/resume/${id}/export`)}
          >
            <FileDown className="h-4 w-4" />
            Export
          </Button>

          {!resume.is_verified && (
            <Button
              variant="outline"
              onClick={() => verifyMutation.mutate()}
              isLoading={verifyMutation.isPending}
              className="gap-2"
            >
              <CheckCircle className="h-4 w-4" />
              Mark as Verified
            </Button>
          )}

          <Button
            variant="destructive"
            className="gap-2 ml-auto"
            onClick={handleDelete}
            isLoading={deleteMutation.isPending}
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </Button>
        </div>

        {/* Low confidence warning */}
        {resume.confidence_score < 85 && !resume.is_verified && (
          <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950">
            <CardContent className="flex items-center gap-3 py-4">
              <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              <div>
                <p className="font-medium">Low confidence score detected</p>
                <p className="text-sm text-muted-foreground">
                  Please review and verify the extracted information before exporting.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* ATS Analysis */}
        {showATS && <ATSAnalysisCard resumeId={resume.id} atsAnalysis={resume.ats_analysis} />}

        {/* AI Improvements */}
        {showAI && <AIImprovementCard resumeId={resume.id} />}

        {/* Resume Editor */}
        <ResumeEditor resume={resume} isEditing={isEditing} />
      </div>
    </AppLayout>
  );
}
