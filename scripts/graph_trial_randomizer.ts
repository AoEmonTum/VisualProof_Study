type Condition = 'proof_property' | 'noproof_property' | 'proof_noproperty' | 'noproof_noproperty';
type Size = 'small' | 'medium' | 'large';

type BaseGraph = { source: string; size: Size; vertices: number };
type Trial = BaseGraph & { condition: Condition };
type TrialPlan = { componentIds: string[]; blocks: Trial[][] };
type DynamicParameters = { listId: string; graphs: BaseGraph[] };
type DynamicAnswer = { parameters?: { graphTrialPlan?: TrialPlan } };
type DynamicInput = {
  answers: Record<string, DynamicAnswer>;
  customParameters: DynamicParameters;
  currentStep: number;
  currentBlock: string;
};

const CONDITIONS: Condition[] = ['proof_property', 'noproof_property', 'proof_noproperty', 'noproof_noproperty'];
const SIZES: Size[] = ['small', 'medium', 'large'];
const BLOCKS_PER_PARTICIPANT = 3;

function shuffle<T>(items: T[]): T[] {
  const result = [...items];
  for (let index = result.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [result[index], result[randomIndex]] = [result[randomIndex], result[index]];
  }
  return result;
}

function assignVisualizations(graphs: BaseGraph[]): Trial[] {
  const bySize = Object.fromEntries(SIZES.map((size) => [size, graphs.filter((graph) => graph.size === size)])) as Record<Size, BaseGraph[]>;
  if (SIZES.some((size) => bySize[size].length !== 6)) throw new Error('Expected exactly six base graphs per size group');

  const highFrequency = new Set(shuffle(CONDITIONS).slice(0, 2));
  const remainingExtras = Object.fromEntries(CONDITIONS.map((condition) => [condition, highFrequency.has(condition) ? 2 : 1])) as Record<Condition, number>;
  const candidatePairs = shuffle(CONDITIONS.flatMap((first) => CONDITIONS.map((second) => [first, second] as const)));
  const extras = {} as Record<Size, [Condition, Condition]>;

  function allocateExtras(sizeIndex: number): boolean {
    if (sizeIndex === SIZES.length) return CONDITIONS.every((condition) => remainingExtras[condition] === 0);
    for (const [first, second] of candidatePairs) {
      const needed = Object.fromEntries(CONDITIONS.map((condition) => [condition, Number(first === condition) + Number(second === condition)])) as Record<Condition, number>;
      if (!CONDITIONS.some((condition) => needed[condition] > remainingExtras[condition])) {
        CONDITIONS.forEach((condition) => { remainingExtras[condition] -= needed[condition]; });
        extras[SIZES[sizeIndex]] = [first, second];
        if (allocateExtras(sizeIndex + 1)) return true;
        CONDITIONS.forEach((condition) => { remainingExtras[condition] += needed[condition]; });
      }
    }
    return false;
  }

  if (!allocateExtras(0)) throw new Error('Could not assign balanced visualization variants');
  return SIZES.flatMap((size) => {
    const conditions = shuffle([...CONDITIONS, ...extras[size]]);
    return shuffle(bySize[size]).map((graph, index) => ({ ...graph, condition: conditions[index] }));
  });
}

function buildBlocks(trials: Trial[]): Trial[][] | null {
  const remaining = Object.fromEntries(SIZES.map((size) => [size, trials.filter((trial) => trial.size === size)])) as Record<Size, Trial[]>;
  const slots = Array.from({ length: BLOCKS_PER_PARTICIPANT }, (_, block) => shuffle([...SIZES, ...SIZES]).map((size) => ({ block, size }))).flat();
  const blocks: Trial[][] = Array.from({ length: BLOCKS_PER_PARTICIPANT }, () => []);
  const conditionsByBlock: Set<Condition>[] = Array.from({ length: BLOCKS_PER_PARTICIPANT }, () => new Set());

  function fill(slotIndex: number): boolean {
    if (slotIndex === slots.length) return conditionsByBlock.every((conditions) => conditions.size === CONDITIONS.length);
    const { block, size } = slots[slotIndex];
    const candidates = shuffle(remaining[size]).sort((first, second) => Number(conditionsByBlock[block].has(first.condition)) - Number(conditionsByBlock[block].has(second.condition)));
    for (const trial of candidates) {
      remaining[size].splice(remaining[size].indexOf(trial), 1);
      blocks[block].push(trial);
      const previousConditions = new Set(conditionsByBlock[block]);
      conditionsByBlock[block].add(trial.condition);
      const futureSizes = slots.slice(slotIndex + 1).filter((slot) => slot.block === block).map((slot) => slot.size);
      const missing = CONDITIONS.filter((condition) => !conditionsByBlock[block].has(condition));
      const feasible = missing.length <= futureSizes.length && missing.every((condition) => futureSizes.some((futureSize) => remaining[futureSize].some((candidate) => candidate.condition === condition)));
      if (feasible && fill(slotIndex + 1)) return true;
      conditionsByBlock[block] = previousConditions;
      blocks[block].pop();
      remaining[size].push(trial);
    }
    return false;
  }

  return fill(0) ? blocks.map((block) => shuffle(block)) : null;
}

function createPlan(parameters: DynamicParameters): TrialPlan {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const blocks = buildBlocks(assignVisualizations(parameters.graphs));
    if (blocks) {
      const componentIds = blocks.flatMap((block) => block.flatMap((trial) => {
        const trialId = `${parameters.listId}_${trial.source}_${trial.condition}`;
        return [`verify_${trialId}`, `confidence_${trialId}`];
      }));
      return { componentIds, blocks };
    }
  }
  throw new Error('Could not construct balanced graph-trial blocks');
}

function getStoredPlan(input: DynamicInput): TrialPlan | undefined {
  const prefix = `${input.currentBlock}_${input.currentStep}_`;
  return Object.entries(input.answers)
    .filter(([identifier]) => identifier.startsWith(prefix))
    .map(([, answer]) => answer.parameters?.graphTrialPlan)
    .find((plan): plan is TrialPlan => plan !== undefined);
}

export default function randomizeGraphTrials(input: DynamicInput) {
  const storedPlan = getStoredPlan(input);
  const plan = storedPlan ?? createPlan(input.customParameters);
  const prefix = `${input.currentBlock}_${input.currentStep}_`;
  const componentIndex = Object.keys(input.answers).filter((identifier) => identifier.startsWith(prefix)).length;
  return {
    component: plan.componentIds[componentIndex] ?? null,
    parameters: { graphTrialPlan: plan },
  };
}
