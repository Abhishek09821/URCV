import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useUpdateResume } from '@/hooks/useResumes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Label } from '@/components/ui/Label';
import type { Resume, ResumeData } from '@/types';
import { Save } from 'lucide-react';

interface ResumeEditorProps {
  resume: Resume;
  isEditing: boolean;
}

export function ResumeEditor({ resume, isEditing }: ResumeEditorProps) {
  const updateMutation = useUpdateResume(resume.id);
  const [activeSection, setActiveSection] = useState<string>('personal');

  const { register, handleSubmit, formState: { isDirty } } = useForm<ResumeData>({
    defaultValues: resume.resume_data,
  });

  const onSubmit = (data: ResumeData) => {
    updateMutation.mutate(data);
  };

  const sections = [
    { id: 'personal', label: 'Personal Info' },
    { id: 'summary', label: 'Summary' },
    { id: 'education', label: 'Education' },
    { id: 'experience', label: 'Experience' },
    { id: 'projects', label: 'Projects' },
    { id: 'skills', label: 'Skills' },
    { id: 'certifications', label: 'Certifications' },
    { id: 'achievements', label: 'Achievements' },
  ];

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Section Tabs */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-2">
            {sections.map((section) => (
              <Button
                key={section.id}
                type="button"
                variant={activeSection === section.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveSection(section.id)}
              >
                {section.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Personal Information */}
      {activeSection === 'personal' && (
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  {...register('personal.full_name')}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  {...register('personal.email')}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  {...register('personal.phone')}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  {...register('personal.location')}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="linkedin">LinkedIn</Label>
                <Input
                  id="linkedin"
                  {...register('personal.linkedin')}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="github">GitHub</Label>
                <Input
                  id="github"
                  {...register('personal.github')}
                  disabled={!isEditing}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary */}
      {activeSection === 'summary' && (
        <Card>
          <CardHeader>
            <CardTitle>Professional Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              {...register('summary')}
              disabled={!isEditing}
              rows={6}
              placeholder="Write a brief professional summary..."
            />
          </CardContent>
        </Card>
      )}

      {/* Skills */}
      {activeSection === 'skills' && (
        <Card>
          <CardHeader>
            <CardTitle>Skills</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Languages</Label>
              <Input
                {...register('skills.languages')}
                disabled={!isEditing}
                placeholder="e.g., Python, JavaScript, Java"
              />
            </div>
            <div className="space-y-2">
              <Label>Frameworks</Label>
              <Input
                {...register('skills.frameworks')}
                disabled={!isEditing}
                placeholder="e.g., React, Django, Spring Boot"
              />
            </div>
            <div className="space-y-2">
              <Label>Tools</Label>
              <Input
                {...register('skills.tools')}
                disabled={!isEditing}
                placeholder="e.g., Git, Docker, AWS"
              />
            </div>
            <div className="space-y-2">
              <Label>Databases</Label>
              <Input
                {...register('skills.databases')}
                disabled={!isEditing}
                placeholder="e.g., PostgreSQL, MongoDB, Redis"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Education, Experience, Projects - Simplified for brevity */}
      {activeSection === 'education' && (
        <Card>
          <CardHeader>
            <CardTitle>Education</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Education editor - Array editing will be implemented with dynamic fields
            </p>
          </CardContent>
        </Card>
      )}

      {activeSection === 'experience' && (
        <Card>
          <CardHeader>
            <CardTitle>Work Experience</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Experience editor - Array editing will be implemented with dynamic fields
            </p>
          </CardContent>
        </Card>
      )}

      {activeSection === 'projects' && (
        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Projects editor - Array editing will be implemented with dynamic fields
            </p>
          </CardContent>
        </Card>
      )}

      {/* Save Button */}
      {isEditing && isDirty && (
        <div className="sticky bottom-4 flex justify-end">
          <Button
            type="submit"
            isLoading={updateMutation.isPending}
            className="gap-2 shadow-lg"
          >
            <Save className="h-4 w-4" />
            Save Changes
          </Button>
        </div>
      )}
    </form>
  );
}
