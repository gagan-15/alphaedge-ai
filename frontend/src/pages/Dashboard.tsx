import Scanner from "./Scanner";

/**
 * AlphaEdge has one primary research workspace. The existing scanner
 * implementation is reused here so Dashboard and Scanner can never drift
 * into two different products.
 */
export default function Dashboard() {
    return <Scanner />;
}
