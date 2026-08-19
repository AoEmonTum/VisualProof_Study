import {
  Box, Button, Collapse, Group, Paper, Progress, Slider, Stack, Text, Title,
} from '@mantine/core';
import { useEffect, useMemo, useState } from 'react';

import type { StoredAnswer, StimulusParams } from '../../../store/types';

type TrialAnswer = {
  decision?: 'yes' | 'no';
  confidence?: number;
};

type GraphTrialParameters = {
  componentName: string;
  trialId: string;
  propertyName: string;
  propertyDefinition: string;
  verificationPrompt: string;
  yesLabel: string;
  noLabel: string;
  graphPath: string;
  graphLabel: string;
  durationMs: number;
  nodeCount: number;
  graphSize: string;
  visualization: string;
  sourceGraph: string;
  phase: 'tutorial' | 'study';
};

function findStoredAnswer(answers: StimulusParams<GraphTrialParameters>['answers'], componentName: string): TrialAnswer | null {
  const stored = Object.values(answers as Record<string, StoredAnswer>).find((entry) => entry.componentName === componentName);
  if (!stored) {
    return null;
  }

  return {
    decision: stored.answer.decision === 'yes' || stored.answer.decision === 'no'
      ? stored.answer.decision
      : undefined,
    confidence: typeof stored.answer.confidence === 'number'
      ? stored.answer.confidence
      : undefined,
  };
}

export default function GraphTrial({ parameters, setAnswer, answers }: StimulusParams<GraphTrialParameters>) {
  const storedAnswer = useMemo(
    () => findStoredAnswer(answers, parameters.componentName),
    [answers, parameters.componentName],
  );

  const [decision, setDecision] = useState<TrialAnswer['decision']>(storedAnswer?.decision ?? undefined);
  const [confidence, setConfidence] = useState<number | undefined>(storedAnswer?.confidence);
  const [confidenceTouched, setConfidenceTouched] = useState<boolean>(storedAnswer?.confidence !== undefined);
  const [graphVisible, setGraphVisible] = useState(true);
  const [remainingMs, setRemainingMs] = useState(parameters.durationMs);

  useEffect(() => {
    setAnswer({
      status: false,
      answers: decision
        ? {
          decision,
          ...(confidenceTouched && confidence !== undefined ? { confidence } : {}),
        }
        : {},
    });
  }, [confidence, confidenceTouched, decision, setAnswer]);

  useEffect(() => {
    const start = Date.now();
    const interval = window.setInterval(() => {
      setRemainingMs(Math.max(0, parameters.durationMs - (Date.now() - start)));
    }, 100);
    const timeout = window.setTimeout(() => {
      setGraphVisible(false);
      setRemainingMs(0);
    }, parameters.durationMs);

    return () => {
      window.clearInterval(interval);
      window.clearTimeout(timeout);
    };
  }, [parameters.durationMs]);

  const confidencePercent = (remainingMs / parameters.durationMs) * 100;
  const canContinue = decision !== undefined && confidenceTouched && confidence !== undefined;

  useEffect(() => {
    if (canContinue) {
      setAnswer({
        status: true,
        answers: {
          decision,
          confidence,
        },
      });
    }
  }, [canContinue, confidence, decision, setAnswer]);

  const handleDecision = (value: 'yes' | 'no') => {
    setDecision(value);
    setConfidence(undefined);
    setConfidenceTouched(false);
  };

  const handleConfidenceChange = (value: number) => {
    setConfidence(value);
    setConfidenceTouched(true);
  };

  const confidenceMarks = [
    { value: 1, label: 'Very low confidence' },
    { value: 2, label: '2' },
    { value: 3, label: '3' },
    { value: 4, label: '4' },
    { value: 5, label: 'Very confident' },
  ];

  return (
    <Stack gap="lg" w="100%">
      <Paper
        radius="xl"
        withBorder
        p="xl"
        style={{
          background: 'linear-gradient(180deg, #f8fbff 0%, #ffffff 100%)',
          borderColor: '#dce7f5',
          boxShadow: '0 18px 44px rgba(15, 23, 42, 0.06)',
        }}
      >
        <Group justify="space-between" align="flex-start" wrap="wrap" mb="xs">
          <Box>
            <Text size="xs" tt="uppercase" fw={700} c="blue.6" style={{ letterSpacing: '0.16em' }}>
              {parameters.propertyName}
            </Text>
            <Title order={3} mt={6} c="gray.9">
              {parameters.verificationPrompt}
            </Title>
            <Text size="sm" c="dimmed" mt={8} maw={780}>
              {parameters.propertyDefinition}
            </Text>
          </Box>

        </Group>

        <Box mb="sm">
          <Progress value={confidencePercent} color="blue" size="sm" radius="xl" />
        </Box>

        <Box
          style={{
            minHeight: 320,
            borderRadius: 20,
            padding: 18,
            background: '#ffffff',
            border: '1px solid #dbe6f3',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {graphVisible ? (
            <img
              src={parameters.graphPath}
              alt={parameters.graphLabel}
              style={{
                display: 'block',
                maxWidth: '100%',
                maxHeight: '60vh',
                objectFit: 'contain',
                transition: 'opacity 220ms ease',
              }}
            />
          ) : (
            <Stack gap={4} align="center" py="xl">
              <Text fw={700} c="gray.7">
                The graph is no longer visible.
              </Text>
              <Text size="sm" c="dimmed">
                Please use your memory to answer the question below.
              </Text>
            </Stack>
          )}
        </Box>
      </Paper>

      <Paper radius="xl" withBorder p="lg" style={{ borderColor: '#dce7f5' }}>
        <Group grow align="stretch">
          <Button
            size="lg"
            variant="default"
            onClick={() => handleDecision('yes')}
            styles={{
              root:
                decision === 'yes'
                  ? {
                      backgroundColor: '#e7f1ff',
                      borderColor: '#4c8bf5',
                      color: '#1f2937',
                    }
                  : {},
            }}
          >
            {parameters.yesLabel}
          </Button>

          <Button
            size="lg"
            variant="default"
            onClick={() => handleDecision('no')}
            styles={{
              root:
                decision === 'no'
                  ? {
                      backgroundColor: '#e7f1ff',
                      borderColor: '#4c8bf5',
                      color: '#1f2937',
                    }
                  : {},
            }}
          >
            {parameters.noLabel}
          </Button>
        </Group>

        <Collapse in={decision !== undefined}>
          <Stack gap="sm" mt="md">
            <Text fw={600} c="gray.8">
              How confident are you in your answer?
            </Text>

            <Slider
              w = "90%"
              mx = "auto"
              min={1}
              max={5}
              step={1}
              value={confidence ?? 3}
              onChange={handleConfidenceChange}
              marks={confidenceMarks}
              label={null}
              styles={{
                markLabel: { fontSize: 12 },
                root: {marginBottom: 10},
              }}
            />
          </Stack>
        </Collapse>
      </Paper>
    </Stack>
  );
}
