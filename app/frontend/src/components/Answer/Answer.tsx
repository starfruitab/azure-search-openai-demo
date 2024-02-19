import { useMemo, useState } from "react";
import { Stack, IconButton, TextField } from "@fluentui/react";
import { Button } from "@fluentui/react-components";

import DOMPurify from "dompurify";

import styles from "./Answer.module.css";

import { ChatAppResponse, getCitationFilePath } from "../../api";
import { parseAnswerToHtml } from "./AnswerParser";
import { AnswerIcon } from "./AnswerIcon";
import { Send28Filled } from "@fluentui/react-icons";
interface Props {
    answer: ChatAppResponse;
    answerIndex: number;
    isSelected?: boolean;
    isStreaming: boolean;
    onCitationClicked: (filePath: string) => void;
    onThoughtProcessClicked: () => void;
    onSupportingContentClicked: () => void;
    onFollowupQuestionClicked?: (question: string) => void;
    showFollowupQuestions?: boolean;
    handleFeedback?: (answerIndex: number, rating: string, feedback: string) => void;
}

export const Answer = ({
    answer,
    answerIndex,
    isSelected,
    isStreaming,
    onCitationClicked,
    onThoughtProcessClicked,
    onSupportingContentClicked,
    onFollowupQuestionClicked,
    showFollowupQuestions,
    handleFeedback
}: Props) => {
    const [feedback, setFeedback] = useState<string>("");
    const [rating, setRating] = useState<string>("");
    const [feedbackSubmitted, setFeedbackSubmitted] = useState<boolean>(false);
    const followupQuestions = answer.choices[0].context.followup_questions;
    const messageContent = answer.choices[0].message.content;
    const parsedAnswer = useMemo(() => parseAnswerToHtml(messageContent, isStreaming, onCitationClicked), [answer]);

    const sanitizedAnswerHtml = DOMPurify.sanitize(parsedAnswer.answerHtml);

    const toggleRating = (clickedRating: string) => {
        if (clickedRating === rating) setRating("");
        else setRating(clickedRating);
    };

    const onEnterPress = (ev: React.KeyboardEvent<Element>) => {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            submitFeedback();
        }
    };

    const submitFeedback = () => {
        if (handleFeedback && rating) {
            handleFeedback(answerIndex, rating, feedback);
            setFeedbackSubmitted(true);
        }
    };

    return (
        <Stack className={`${styles.answerContainer} ${isSelected && styles.selected}`} verticalAlign="space-between">
            <Stack.Item>
                <Stack horizontal horizontalAlign="space-between">
                    <AnswerIcon />
                    <div>
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "Lightbulb" }}
                            title="Show thought process"
                            ariaLabel="Show thought process"
                            onClick={() => onThoughtProcessClicked()}
                            disabled={!answer.choices[0].context.thoughts?.length}
                        />
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "ClipboardList" }}
                            title="Show supporting content"
                            ariaLabel="Show supporting content"
                            onClick={() => onSupportingContentClicked()}
                            disabled={!answer.choices[0].context.data_points?.length}
                        />
                    </div>
                </Stack>
            </Stack.Item>

            <Stack.Item grow>
                <div className={styles.answerText} dangerouslySetInnerHTML={{ __html: sanitizedAnswerHtml }}></div>
            </Stack.Item>

            {!!parsedAnswer.citations.length && (
                <Stack.Item>
                    <Stack horizontal wrap tokens={{ childrenGap: 5 }}>
                        <span className={styles.citationLearnMore}>Source:</span>
                        {parsedAnswer.citations.map((citation, index) => {
                            const [citationPath, citationTitle] = citation.split("|").map(part => part.trim());
                            const linkTitle = citationTitle || citationPath;
                            const path = getCitationFilePath(citationPath);

                            return (
                                <a key={index} className={styles.citation} title={linkTitle} onClick={() => onCitationClicked(path)}>
                                    {`${index + 1}. ${linkTitle}`}
                                </a>
                            );
                        })}
                    </Stack>
                </Stack.Item>
            )}

            {!!followupQuestions?.length && showFollowupQuestions && onFollowupQuestionClicked && (
                <Stack.Item>
                    <Stack horizontal wrap className={`${!!parsedAnswer.citations.length ? styles.followupQuestionsList : ""}`} tokens={{ childrenGap: 6 }}>
                        <span className={styles.followupQuestionLearnMore}>Follow-up questions:</span>
                        {followupQuestions.map((x, i) => {
                            return (
                                <a key={i} className={styles.followupQuestion} title={x} onClick={() => onFollowupQuestionClicked(x)}>
                                    {`${x}`}
                                </a>
                            );
                        })}
                    </Stack>
                </Stack.Item>
            )}
            {!isStreaming && (
                <div className={styles.ratingButtons}>
                    <IconButton
                        style={{
                            color: rating === "good" ? "green" : "black",
                            backgroundColor: rating === "good" ? "#DDFDCE" : ""
                        }}
                        iconProps={{ iconName: "Like" }}
                        title="Approve answer"
                        ariaLabel="Approve answer"
                        onClick={() => toggleRating("good")}
                        disabled={!answer.choices[0].context.thoughts?.length}
                    />
                    <IconButton
                        style={{
                            color: rating === "bad" ? "red" : "black",
                            backgroundColor: rating === "bad" ? "#FDCECE" : ""
                        }}
                        iconProps={{ iconName: "Dislike" }}
                        title="Reject answer"
                        ariaLabel="Reject answer"
                        onClick={() => toggleRating("bad")}
                        disabled={!answer.choices[0].context.data_points?.length}
                    />
                </div>
            )}
            {rating && !feedbackSubmitted && (
                <Stack horizontal className={styles.feedbackWrapper} style={rating === "good" ? { borderColor: "#9BF085" } : { borderColor: "#FDCECE" }}>
                    <TextField
                        className={styles.feedbackField}
                        placeholder={"Enter optional feedback"}
                        multiline
                        resizable={false}
                        borderless
                        onChange={(ev, newValue) => setFeedback(newValue || "")}
                        onKeyDown={onEnterPress}
                    />
                    <div className={styles.feedbackSubmitButton}>
                        <Button size="large" icon={<Send28Filled primaryFill={rating === "good" ? "green" : "red"} />} onClick={submitFeedback} />
                    </div>
                </Stack>
            )}
            {feedbackSubmitted && <div className={styles.answerText}>Thank you for your feedback!</div>}
        </Stack>
    );
};
