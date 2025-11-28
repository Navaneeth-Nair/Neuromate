import { MessageCircle, Eye, ArrowRight, TrendingUp } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface TrendingTopicCardProps {
    topic: {
        id: number;
        tag: string;
        title: string;
        description: string;
        replies: number;
        views: number;
        growth: number;
        isHot: boolean;
    };
}

const TrendingTopicCard = ({ topic }: TrendingTopicCardProps) => {
    return (
        <Card className="hover:shadow-lg transition-all hover:border-primary/50 group flex flex-col h-full overflow-hidden relative">
            {topic.isHot && (
                <div className="absolute top-0 right-0 bg-orange-500 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg z-10 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3" /> HOT
                </div>
            )}

            <CardHeader className="pb-3 pt-5">
                <div className="flex justify-between items-start mb-2">
                    <Badge variant="secondary" className="mb-2 bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
                        {topic.tag}
                    </Badge>
                </div>
                <h3 className="text-lg font-bold group-hover:text-primary transition-colors line-clamp-2">
                    {topic.title}
                </h3>
            </CardHeader>

            <CardContent className="flex-1 pb-3">
                <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
                    {topic.description}
                </p>

                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <MessageCircle className="h-3 w-3" />
                        <span>{topic.replies} replies</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        <span>{topic.views > 1000 ? `${(topic.views / 1000).toFixed(1)}k` : topic.views} views</span>
                    </div>
                    <div className="flex items-center gap-1 text-green-600 font-medium">
                        <TrendingUp className="h-3 w-3" />
                        <span>+{topic.growth}% this week</span>
                    </div>
                </div>
            </CardContent>

            <CardFooter className="pt-2 bg-muted/30">
                <Button
                    className="w-full gap-2 group-hover:bg-primary group-hover:text-primary-foreground transition-all"
                    variant="ghost"
                    size="sm"
                >
                    Join Discussion <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
            </CardFooter>
        </Card>
    );
};

export default TrendingTopicCard;
