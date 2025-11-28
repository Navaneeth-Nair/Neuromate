import { Users, Clock, Trophy, ArrowRight } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface ChallengeCardProps {
    challenge: {
        id: number;
        title: string;
        description: string;
        duration: string;
        level: "Easy" | "Medium" | "Hard";
        participants: number;
        category: string;
        isJoined: boolean;
        progress?: number;
        streak?: number;
    };
}

const ChallengeCard = ({ challenge }: ChallengeCardProps) => {
    const getLevelColor = (level: string) => {
        switch (level) {
            case "Easy": return "bg-green-500/10 text-green-600 border-green-500/20";
            case "Medium": return "bg-yellow-500/10 text-yellow-600 border-yellow-500/20";
            case "Hard": return "bg-red-500/10 text-red-600 border-red-500/20";
            default: return "bg-muted text-muted-foreground";
        }
    };

    return (
        <Card className="hover:shadow-lg transition-all hover:border-primary/50 group flex flex-col h-full">
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start mb-2">
                    <Badge variant="outline" className="mb-2">{challenge.category}</Badge>
                    <Badge variant="outline" className={getLevelColor(challenge.level)}>{challenge.level}</Badge>
                </div>
                <CardTitle className="text-xl group-hover:text-primary transition-colors">
                    {challenge.title}
                </CardTitle>
            </CardHeader>

            <CardContent className="flex-1 pb-3">
                <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
                    {challenge.description}
                </p>

                <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                    <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{challenge.duration}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        <span>{challenge.participants.toLocaleString()}</span>
                    </div>
                </div>

                {challenge.isJoined && challenge.progress !== undefined && (
                    <div className="space-y-2 mt-2">
                        <div className="flex justify-between text-xs font-medium">
                            <span>Progress</span>
                            <span>{challenge.progress}%</span>
                        </div>
                        <Progress value={challenge.progress} className="h-2" />
                        {challenge.streak !== undefined && (
                            <div className="flex items-center gap-1 text-xs text-orange-500 font-medium mt-1">
                                <Trophy className="h-3 w-3" />
                                <span>{challenge.streak} day streak!</span>
                            </div>
                        )}
                    </div>
                )}
            </CardContent>

            <CardFooter className="pt-0">
                <Button
                    className={`w-full gap-2 ${challenge.isJoined ? "bg-secondary text-secondary-foreground hover:bg-secondary/80" : ""}`}
                    variant={challenge.isJoined ? "secondary" : "default"}
                >
                    {challenge.isJoined ? (
                        <>Continue Challenge <ArrowRight className="h-4 w-4" /></>
                    ) : (
                        <>Join Challenge</>
                    )}
                </Button>
            </CardFooter>
        </Card>
    );
};

export default ChallengeCard;
