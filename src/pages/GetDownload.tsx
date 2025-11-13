import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "@/hooks/useAuth";

const EXTERNAL_LINK = "https://github.com/Navaneeth-Nair/Mindmate";

const GetDownload = () => {
  const { session, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !session) {
      navigate("/login");
    } else if (session) {
      window.location.href = EXTERNAL_LINK;
    }
  }, [session, loading, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="glass-card p-12 rounded-2xl shadow-xl text-center space-y-8">
        <h1 className="text-3xl font-heading font-bold mb-4">Redirecting to Download...</h1>
        <p className="text-lg text-muted-foreground mb-6">If you are not redirected, <a href={EXTERNAL_LINK} className="text-primary underline">click here</a>.</p>
      </div>
    </div>
  );
};

export default GetDownload;
