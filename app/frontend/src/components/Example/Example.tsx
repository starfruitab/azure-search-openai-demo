import styles from "./Example.module.css";

interface Props {
    text: string;
    value: string;
    onClick: (value: string) => void;
}

export const Example = ({ text, value, onClick }: Props) => {
    return (
        <li className={styles.example} onClick={() => onClick(value)}>
            <p className={styles.exampleText}>{text}</p>
        </li>
    );
};
