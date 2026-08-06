import { useState } from 'react';
import { useAnalyzeATS } from '@/hooks/useATS';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import type { ATSAnalysis } from '@/types';
import { RefreshCw, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { getScoreColor } from '@/lib/utils';

interface ATSAnalysisCardProps {
  resumeId: string;
  atsAnalysis?: ATSAnalysis;
}

export function ATSAnalysisCard({ resumeId, atsAnalysis: initialAnalysis }: ATSAnalysisCardProps) {
  const [analysis, setAnalysis] = useState<ATSAnalysis | undefined>(initialAnalysis);
  const analyzeMutation = useAnalyzeATS(resumeId);

  const handleAnalyze = async () => {
    analyzeMutation.mutate(undefined, {
      onSuccess: (data) => setAnalysis(data),
    });
  };

  if (!analysis && !analyzeMutation.isPending) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>ATS Analysis</CardTitle>
          <CardDescription>
            Analyze your resume's compatibility with Applicant Tracking Systems
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleAnalyze} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Run ATS Analysis
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (analyzeMutation.isPending) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>ATS Analysis</CardTitle>
        </CardHeader>
        <CardContent className="py-12">
          <div className="flex flex-col items-center gap-4">
            <LoadingSpinner size="lg" />
            <p className="text-sm text-muted-foreground">Analyzing your resume...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) return null;

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'medium':
        return <Info className="h-4 w-4 text-yellow-600" />;
      default:
        return <CheckCircle2 className="h-4 w-4 text-blue-600" />;
    }
  };

  const getPriorityVariant = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'destructive' as const;
      case 'medium':
        return 'warning' as const;
      default:
        return 'info' as const;
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>ATS Analysis</CardTitle>
          <CardDescription>Your resume's ATS compatibility score</CardDescription>
        </div>
        <Button variant="outline" size="sm" onClick={handleAnalyze} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Re-analyze
        </Button>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Score */}
        <div className="text-center">
          <div className={`text-5xl font-bold ${getScoreColor(analysis.overall_score)}`}>
            {analysis.overall_score}%
          </div>
          <p className="mt-2 text-sm text-muted-foreground">Overall ATS Score</p>
        </div>

        {/* Category Scores */}
        <div className="space-y-4">
          <h3 className="font-semibold">Category Breakdown</h3>
          {Object.entries(analysis.categories).map(([key, category]) => {
            const percentage = Math.round((category.score / category.max_score) * 100);
            return (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="capitalize">
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span className={getScoreColor(percentage)}>
                    {category.score}/{category.max_score}
                  </span>
                </div>
                <Progress value={percentage} className="h-2" />
                {category.details.length > 0 && (
                  <ul className="ml-4 space-y-1 text-xs text-muted-foreground">
                    {category.details.map((detail, idx) => (
                      <li key={idx}>• {detail}</li>
                    ))}
                  </ul>
                )}
              </div>
            );
          })}
        </div>

        {/* Keywords */}
        {analysis.keywords_found.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-semibold">Keywords Found</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.keywords_found.map((keyword, idx) => (
                <Badge key={idx} variant="success">
                  {keyword}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {analysis.keywords_missing.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-semibold">Missing Keywords</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.keywords_missing.map((keyword, idx) => (
                <Badge key={idx} variant="warning">
                  {keyword}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Suggestions */}
        {analysis.suggestions.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold">Improvement Suggestions</h3>
            <div className="space-y-3">
              {analysis.suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className="rounded-lg border p-4 space-y-2"
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      {getPriorityIcon(suggestion.priority)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={getPriorityVariant(suggestion.priority)} className="text-xs">
                          {suggestion.priority}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{suggestion.category}</span>
                      </div>
                      <p className="text-sm font-medium">{suggestion.suggestion}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Impact: {suggestion.impact}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
