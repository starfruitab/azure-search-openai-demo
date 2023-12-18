import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    { text: "Set Photocells KTx manually", value: "Set Photocells KTx manually" },
    // { text: "How do I check photocell of the CSU frame?", value: "How do I check photocell of the CSU frame?" },
    { text: "How do I lubricate the linear unit?", value: "How do I lubricate the linear unit?" },
    { text: "Describe the setting sequence of CAU", value: "Describe the setting sequence of CAU" },
    { text: "Check belt of the Servo lift discharger", value: "Check belt of the Servo Lift Discharger" }
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <Example key={i} text={x.text} value={x.value} onClick={onExampleClicked} />
            ))}
        </ul>
    );
};
