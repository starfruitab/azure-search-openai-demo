import React, { useEffect, useState } from "react";
import { Spinner } from "@fluentui/react";
import styles from "./LoadingOverlay.module.css";

export const LoadingOverlay = () => {
    const [showLoading, setShowLoading] = useState(false);

    useEffect(() => {
        setShowLoading(true);
        const timeout = setTimeout(() => setShowLoading(false), 2500);

        return () => clearTimeout(timeout);
    }, []);

    return !showLoading ? null : (
        <div className={styles.container}>
            <div className={styles.spinner}>
                <Spinner label="Loading manual" />
            </div>
        </div>
    );
};
