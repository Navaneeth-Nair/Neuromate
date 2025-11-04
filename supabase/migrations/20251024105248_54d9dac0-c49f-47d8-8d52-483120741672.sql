-- Create beta_signups table for storing beta testing requests
CREATE TABLE public.beta_signups (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.beta_signups ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anyone to insert beta signups (public form)
CREATE POLICY "Anyone can submit beta signup requests" 
ON public.beta_signups 
FOR INSERT 
WITH CHECK (true);

-- Create index for email lookups
CREATE INDEX idx_beta_signups_email ON public.beta_signups(email);

-- Add comment
COMMENT ON TABLE public.beta_signups IS 'Stores beta testing signup requests from users';