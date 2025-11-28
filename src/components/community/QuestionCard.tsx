import { ArrowBigUp, MessageSquare, Bookmark } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface QuestionCardProps {
    question: {
        id: number;
        title: string;
        description: string;
        tags: string[];
        author: string;
        avatar: string;
        timeAgo: string;
        upvotes: number;
        answers: number;
        isAnswered: boolean;
    };
}

const QuestionCard = ({ question }: QuestionCardProps) => {
    return (
        <Card className="hover:border-primary/50 transition-colors cursor-pointer group">
            <div className="flex">
                {/* Upvote Section */}
                <div className="flex flex-col items-center p-4 gap-1 bg-muted/30 border-r border-border/50 min-w-[60px]">
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-primary hover:bg-primary/10">
                        <ArrowBigUp className="h-6 w-6" />
                    </Button>
                    <span className="font-bold text-sm">{question.upvotes}</span>
                </div>

                {/* Content Section */}
                <div className="flex-1">
                    <CardHeader className="p-4 pb-2">
                        <div className="flex justify-between items-start gap-4">
                            <div>
                                <h3 className="text-lg font-semibold group-hover:text-primary transition-colors line-clamp-2">
                                    {question.title}
                                </h3>
                                <div className="flex gap-2 mt-2">
                                    {question.tags.map((tag) => (
                                        <Badge key={tag} variant="secondary" className="text-xs px-2 py-0.5 h-5">
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                            {question.isAnswered && (
                                <Badge variant="outline" className="bg-green-500/10 text-green-600 border-green-500/20 whitespace-nowrap">
                                    Answered
                                </Badge>
                            )}
                        </div>
                    </CardHeader>

                    <CardContent className="p-4 py-2">
                        <p className="text-muted-foreground text-sm line-clamp-2">
                            {question.description}
                        </p>
                    </CardContent>

                    <CardFooter className="p-4 pt-2 flex justify-between items-center text-xs text-muted-foreground">
                        <div className="flex items-center gap-2">
                            <Avatar className="h-5 w-5">
                                <AvatarImage src={question.avatar} />
                                <AvatarFallback>{question.author[0]}</AvatarFallback>
                            </Avatar>
                            <span>{question.author}</span>
                            <span>•</span>
                            <span>{question.timeAgo}</span>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-1 hover:text-foreground transition-colors">
                                <MessageSquare className="h-4 w-4" />
                                <span>{question.answers} answers</span>
                            </div>
                            <Button variant="ghost" size="icon" className="h-6 w-6">
                                <Bookmark className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardFooter>
                </div>
            </div>
        </Card>
    );
};

export default QuestionCard;
