import { renderToStaticMarkup } from "react-dom/server";
import { getCitationFilePath } from "../../api";

type HtmlParsedAnswer = {
    answerHtml: string;
    citations: string[];
};

export function parseAnswerToHtml(answer: string, isStreaming: boolean, onCitationClicked: (citationFilePath: string) => void): HtmlParsedAnswer {
    const citations: string[] = [];

    // trim any whitespace from the end of the answer after removing follow-up questions
    let parsedAnswer = answer.trim();

    // Omit a citation that is still being typed during streaming
    if (isStreaming) {
        let lastIndex = parsedAnswer.length;
        for (let i = parsedAnswer.length - 1; i >= 0; i--) {
            if (parsedAnswer[i] === "]") {
                break;
            } else if (parsedAnswer[i] === "[") {
                lastIndex = i;
                break;
            }
        }
        const truncatedAnswer = parsedAnswer.substring(0, lastIndex);
        parsedAnswer = truncatedAnswer;
    }

    const parts = parsedAnswer.split(/\[([^\]]+)\]/g);

    const fragments: string[] = parts.map((part, index) => {
        if (index % 2 === 0) {
            return part;
        } else {
            let citation = part;
            let citationIndex: number;
            if (citations.includes(citation)) {
                citationIndex = citations.indexOf(citation) + 1;
            } else {
                citations.push(citation);
                citationIndex = citations.length;
            }

            const [citationIdentifier] = citation.split("|").map(s => s.trim());
            const path = getCitationFilePath(citationIdentifier);

            return renderToStaticMarkup(
                <a className="supContainer" title={citation} onClick={() => onCitationClicked(path)}>
                    <sup>{citationIndex}</sup>
                </a>
            );
        }
    });

    return {
        answerHtml: fragments.join(""),
        citations
    };
}
