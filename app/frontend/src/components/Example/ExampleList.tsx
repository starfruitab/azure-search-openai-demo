import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    { text: "Describe the steps to Change Inductive Switch of the CSU Frame.", value: "Describe the steps to Change Inductive Switch of the CSU Frame." },
    // { text: "How do I check photocell of the CSU frame?", value: "How do I check photocell of the CSU frame?" },
    { text: "Describe the steps to lubricate the linear unit", value: "Describe the steps to lubricate the linear unit" }
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
