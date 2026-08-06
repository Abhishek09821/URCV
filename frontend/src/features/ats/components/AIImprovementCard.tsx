import { useState } from 'react';
import { useImproveSection, useApplyImprovement } from '@/hooks/useAI';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Label } from '@/components/ui/Label';
import type { AIImprovement, AIImprovementRequest } from '@/types';
import { Sparkles, Check, X } from 'lucide-react';

interface AIImprovementCardProps {
  resumeId: string;
}

export function AIImprovementCard({ resumeId }: AIImprovementCardProps) {
  const [improvement, setImprovement] = useState<AIImprovement | null>(null);
  const [selectedSection, setSelectedSection] = useState<AIImprovementRequest['section_type']>('summary');
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['grammar', 'action_verbs']);
  
  const improveMutation = useImproveSection(resumeId);
  const applyMutation = useApplyImprovement(resumeId);

  const sectionOptions: AIImprovementRequest['section_type'][] = ['summary', 'experience', 'projects', 'achievements'];
  const improvementTypes = [
    { value: 'grammar', label: 'Grammar & Spelling' },
    { value: 'action_verbs', label: 'Action Verbs' },
    { value: 'professional_tone', label: 'Professional Tone' },
    { value: 'clarity', label: 'Clarity & Conciseness' },
  ];

  const handleGenerate = () => {
    const request: AIImprovementRequest = {
      section_type: selectedSection,
      improvement_types: selectedTypes,
    };

    improveMutation.mutate(request, {
      onSuccess: (data) => setImprovement(data),
    });
  };

  const handleApply = () => {
    if (improvement) {
      applyMutation.mutate(improvement.id, {
        onSuccess: () => setImprovement(null),
      });
    }
  };

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Improvements
        </CardTitle>
        <CardDescription>
          Let AI suggest improvements to your resume content
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Section Selection */}
        <div className="space-y-2">
          <Label>Select Section to Improve</Label>
          <div className="flex flex-wrap gap-2">
            {sectionOptions.map((section) => (
              <Button
                key={section}
                type="button"
                variant={selectedSection === section ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedSection(section)}
                className="capitalize"
              >
                {section}
              </Button>
            ))}
          </div>
        </div>

        {/* Improvement Types */}
        <div className="space-y-2">
          <Label>Improvement Types</Label>
          <div className="flex flex-wrap gap-2">
            {improvementTypes.map((type) => (
              <Button
                key={type.value}
                type="button"
                variant={selectedTypes.includes(type.value) ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleType(type.value)}
              >
                {type.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          isLoading={improveMutation.isPending}
          disabled={selectedTypes.length === 0}
          className="gap-2 w-full"
        >
          <Sparkles className="h-4 w-4" />
          Generate AI Improvement
        </Button>

        {/* Loading State */}
        {improveMutation.isPending && (
          <div className="flex flex-col items-center gap-4 py-8">
            <LoadingSpinner size="lg" />
            <p className="text-sm text-muted-foreground">AI is analyzing and improving...</p>
          </div>
        )}

        {/* Improvement Result */}
        {improvement && !improveMutation.isPending && (
          <div className="space-y-4 rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <Badge variant="info" className="gap-1">
                <Sparkles className="h-3 w-3" />
                AI Suggestion
              </Badge>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setImprovement(null)}
                  className="gap-1"
                >
                  <X className="h-3 w-3" />
                  Reject
                </Button>
                <Button
                  size="sm"
                  onClick={handleApply}
                  isLoading={applyMutation.isPending}
                  className="gap-1"
                >
                  <Check className="h-3 w-3" />
                  Apply
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1">Original</p>
                <div className="rounded bg-muted p-3 text-sm">
                  {improvement.original_content}
                </div>
              </div>

              <div>
                <p className="text-xs font-medium text-green-600 mb-1">Improved</p>
                <div className="rounded border-2 border-green-200 bg-green-50 p-3 text-sm dark:border-green-900 dark:bg-green-950">
                  {improvement.improved_content}
                </div>
              </div>
            </div>

            <p className="text-xs text-muted-foreground">
              <strong>Note:</strong> AI suggestions preserve your facts but enhance presentation.
              Review before applying.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
