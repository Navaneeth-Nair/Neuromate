import { auth } from "@/integrations/firebase/client";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { Button } from "@/components/ui/button";
import { useNavigate, useLocation } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleGoogleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      navigate("/download");
    } catch (error: unknown) {
      if (error instanceof Error) {
        alert(`Login failed: ${error.message}`);
      } else {
        alert("Login failed!");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-hero">
      <div className="glass-card p-12 rounded-2xl shadow-xl text-center space-y-8">
        <h1 className="text-4xl font-heading font-bold mb-4">Login to Download</h1>
        <p className="text-lg text-muted-foreground mb-6">Sign in with Google to access the NeuroMate download</p>
        <Button size="lg" className="bg-gradient-primary hover-glow" onClick={handleGoogleLogin}>
          Continue with Google
        </Button>
      </div>
    </div>
  );
};

export default Login;
