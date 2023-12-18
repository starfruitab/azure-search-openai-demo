import styles from "./MachineSelect.module.css";
import TT3 from "../../assets/TT3.png";
import { Select } from "@fluentui/react-components";

export const MachineSelect = () => {
    return (
        <div className={styles.machineSelectContainer}>
            <img src={TT3} alt="TT3" className={styles.machineImage} />
            <div className={styles.machineSelectField}>
                <Select defaultValue="Green" className={styles.machineSelect}>
                    <option>TT3/2000</option>
                </Select>
            </div>
        </div>
    );
};
