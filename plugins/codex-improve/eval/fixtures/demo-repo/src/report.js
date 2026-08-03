export function writeReport(rows, output) {
  output.write(rows.map((row) => JSON.stringify(row)).join("\n"));
}
