import { useEffect, useMemo, useState, useRef } from "react";
import * as d3 from "d3";
import { fetchMC } from "../api";

const MIN_PATHS = 100;
const MAX_PATHS = 2000000;
const DEFAULT_PATHS = 100000;

function toInt(value, fallback) {
  const num = Number(value);
  if (!Number.isFinite(num)) {
    return fallback;
  }
  return Math.round(num);
}

function clampInt(value, min, max, fallback) {
  const num = toInt(value, fallback);
  return Math.min(max, Math.max(min, num));
}

/**
 * @param {{
 *  basePayload: {
 *    spot: number,
 *    strike: number,
 *    rate: number,
 *    vol: number,
 *    time: number,
 *    dividend: number,
 *    option_type: string,
 *    method: string,
 *    num_paths: number,
 *    seed: number,
 *    antithetic: boolean
 *  }
 * }} props
 */
export default function MonteCarloConvergence({ basePayload }) {
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(false);
  const svgRef = useRef(null);

  const pathCounts = useMemo(() => {
    const maxN = clampInt(basePayload?.num_paths, MIN_PATHS, MAX_PATHS, DEFAULT_PATHS);
    // choose ~8 logarithmically spaced points up to maxN
    const steps = [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000];
    return steps.filter((n) => n <= maxN);
  }, [basePayload.num_paths]);

  useEffect(() => {
    let mounted = true;
    async function run() {
      setLoading(true);
      const results = [];
      for (const n of pathCounts) {
        try {
          const res = await fetchMC({ ...basePayload, num_paths: n });
          if (!mounted) return;
          results.push({ n, price: res.price, stderr: res.stderr });
          setSeries([...results]);
        } catch (e) {
          // stop on error
          break;
        }
      }
      setLoading(false);
    }

    run();
    return () => (mounted = false);
  }, [basePayload, pathCounts]);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const width = 720;
    const height = 360;
    const margin = { top: 28, right: 30, bottom: 44, left: 56 };
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    if (!series || series.length === 0) {
      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("class", "chart-empty")
        .text(loading ? "Running MC..." : "No convergence data yet");
      return;
    }

    const x = d3
      .scaleLog()
      .domain(d3.extent(series, (d) => d.n))
      .range([margin.left, width - margin.right]);

    const y = d3
      .scaleLinear()
      .domain(d3.extent(series, (d) => d.price))
      .nice()
      .range([height - margin.bottom, margin.top]);

    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(6, ",.0f").tickSize(0));

    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).tickSize(0));

    const line = d3
      .line()
      .x((d) => x(d.n))
      .y((d) => y(d.price))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(series)
      .attr("fill", "none")
      .attr("stroke", "#111")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Dots only for convergence, no connecting line.
    svg
      .selectAll(".dot")
      .data(series)
      .enter()
      .append("circle")
      .attr("class", "dot")
      .attr("cx", (d) => x(d.n))
      .attr("cy", (d) => y(d.price))
      .attr("r", 4)
      .attr("fill", "#111");

    svg
      .append("text")
      .attr("class", "chart-title")
      .attr("x", margin.left)
      .attr("y", 18)
      .text("Price convergence vs MC paths");
  }, [series, loading]);

  return <svg ref={svgRef} className="chart" role="img" />;
}
