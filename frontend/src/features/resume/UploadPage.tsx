import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { useUploadResume } from '@/hooks/useResumes';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Upload, FileText, X } from 'lucide-react';
import { APP_CONFIG } from '@/lib/config';
import { formatFileSize } from '@/lib/utils';
import toast from 'react-hot-toast';

export function UploadPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const uploadMutation = useUploadResume();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      if (file.size > APP_CONFIG.MAX_FILE_SIZE) {
        toast.error(`File too large. Maximum size is ${formatFileSize(APP_CONFIG.MAX_FILE_SIZE)}`);
        return;
      }
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: APP_CONFIG.ACCEPTED_FILE_TYPES,
    maxFiles: 1,
    multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    uploadMutation.mutate(selectedFile, {
      onSuccess: (resume) => {
        navigate(`/resume/${resume.id}`);
      },
    });
  };

  return (
    <AppLayout>
      <div className="mx-auto max-w-2xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold">Upload Resume</h1>
          <p className="text-muted-foreground">Upload your PDF resume to get started</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Select File</CardTitle>
            <CardDescription>
              Upload a PDF resume to parse and analyze (max {formatFileSize(APP_CONFIG.MAX_FILE_SIZE)})
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Dropzone */}
            {!selectedFile ? (
              <div
                {...getRootProps()}
                className={`cursor-pointer rounded-lg border-2 border-dashed p-12 text-center transition-colors ${
                  isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-muted-foreground/25 hover:border-primary hover:bg-accent'
                }`}
              >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                    <Upload className="h-8 w-8 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">
                      {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                    </p>
                    <p className="text-sm text-muted-foreground">or click to browse files</p>
                  </div>
                  <p className="text-xs text-muted-foreground">PDF files only</p>
                </div>
              </div>
            ) : (
              /* Selected File Preview */
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSelectedFile(null)}
                    aria-label="Remove file"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                onClick={handleUpload}
                disabled={!selectedFile}
                isLoading={uploadMutation.isPending}
                className="flex-1"
              >
                Upload & Parse Resume
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate('/dashboard')}
                disabled={uploadMutation.isPending}
              >
                Cancel
              </Button>
            </div>

            {/* Info */}
            <div className="rounded-lg bg-muted p-4 text-sm">
              <h4 className="mb-2 font-medium">What happens next?</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Your resume will be parsed and analyzed</li>
                <li>• We'll extract all sections with confidence scores</li>
                <li>• You can review and verify the parsed data</li>
                <li>• Get ATS analysis and AI improvements</li>
                <li>• Export to any template format</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
