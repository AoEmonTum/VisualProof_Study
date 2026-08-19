import {
  AppShell, Box, Button, Flex,
} from '@mantine/core';
import { Outlet } from 'react-router';
import {
  useEffect, useMemo, useRef,
  useState,
} from 'react';
import type { CSSProperties } from 'react';
import { IconArrowLeft } from '@tabler/icons-react';
import { AppAside } from './interface/AppAside';
import { AppHeader } from './interface/AppHeader';
import { AppNavBar } from './interface/AppNavBar';
import { HelpModal } from './interface/HelpModal';
import { AlertModal } from './interface/AlertModal';
import { ConfigVersionWarningModal } from './interface/ConfigVersionWarningModal';
import { useStudyConfig } from '../store/hooks/useStudyConfig';
import { WindowEventsContext } from '../store/hooks/useWindowEvents';
import { useStoreSelector, useStoreDispatch, useStoreActions } from '../store/store';
import { AnalysisFooter } from './interface/AnalysisFooter';
import { useIsAnalysis } from '../store/hooks/useIsAnalysis';
import { studyComponentToIndividualComponent } from '../utils/handleComponentInheritance';
import { useCurrentComponent } from '../routes/utils';
import { useFetchStylesheet } from '../utils/fetchStylesheet';
import { RecordingContext, useRecording } from '../store/hooks/useRecording';
import { ScreenRecordingRejection } from './interface/ScreenRecordingRejection';
import { ReplayContext, useReplay } from '../store/hooks/useReplay';
import { DeviceWarning } from './interface/DeviceWarning';
import { handleBeforeUnload, shouldConfirmTabClose } from '../utils/closeTabConfirmation';

const STUDY_BROWSER_WIDTH = 360;

export function StepRenderer() {
  const windowEvents = useRef<never[]>([]);
  const dispatch = useStoreDispatch();
  const { toggleStudyBrowser } = useStoreActions();

  const isAnalysis = useIsAnalysis();
  const studyConfig = useStudyConfig();
  const currentComponent = useCurrentComponent();

  const componentConfig = useMemo(() => studyComponentToIndividualComponent(studyConfig.components[currentComponent] || {}, studyConfig), [currentComponent, studyConfig]);

  useFetchStylesheet(studyConfig?.uiConfig.stylesheetPath);

  const showStudyBrowser = useStoreSelector((state) => state.showStudyBrowser);
  const modes = useStoreSelector((state) => state.modes);
  const isCompleted = useStoreSelector((state) => state.completed);
  const isSubmittingFinal = useStoreSelector((state) => state.isSubmittingFinal);

  const screenRecording = useRecording();
  const replay = useReplay();

  const { isRejected: isScreenRecordingUserRejected } = screenRecording;

  const analysisHasScreenRecording = useStoreSelector((state) => state.analysisHasScreenRecording);
  const analysisCanPlayScreenRecording = useStoreSelector((state) => state.analysisCanPlayScreenRecording);

  const { developmentModeEnabled, dataCollectionEnabled } = useMemo(() => modes, [modes]);

  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  // No default value for withSidebar since it's a required field in uiConfig
  const sidebarOpen = useMemo(() => (((analysisHasScreenRecording && analysisCanPlayScreenRecording) || currentComponent === 'end') ? false : (componentConfig.withSidebar ?? studyConfig.uiConfig.withSidebar)), [analysisHasScreenRecording, analysisCanPlayScreenRecording, currentComponent, componentConfig.withSidebar, studyConfig.uiConfig.withSidebar]);
  const sidebarWidth = windowWidth < 740 ? 0 : windowWidth * windowWidth * 0.0001;
  const showTitleBar = useMemo(() => componentConfig.showTitleBar ?? studyConfig.uiConfig.showTitleBar ?? true, [componentConfig, studyConfig]);

  const asideOpen = useMemo(() => developmentModeEnabled && showStudyBrowser, [developmentModeEnabled, showStudyBrowser]);
  const rowMaxWidth = useMemo(() => (asideOpen ? `max(0px, calc(100% - ${STUDY_BROWSER_WIDTH}px))` : '100%'), [asideOpen]);
  const shouldConfirmClose = useMemo(
    () => shouldConfirmTabClose(
      isAnalysis,
      currentComponent,
      developmentModeEnabled,
      isCompleted,
      dataCollectionEnabled,
      isSubmittingFinal,
    ),
    [isAnalysis, currentComponent, developmentModeEnabled, isCompleted, dataCollectionEnabled, isSubmittingFinal],
  );

  const [hasAudio, setHasAudio] = useState<boolean>();

  useEffect(() => {
    if (!shouldConfirmClose) {
      return undefined;
    }

    const beforeUnloadListener = (event: BeforeUnloadEvent) => {
      handleBeforeUnload(event);
    };

    window.addEventListener('beforeunload', beforeUnloadListener);
    return () => {
      window.removeEventListener('beforeunload', beforeUnloadListener);
    };
  }, [shouldConfirmClose]);

  return (
    <WindowEventsContext.Provider value={windowEvents}>
      <RecordingContext.Provider value={screenRecording}>
        <ReplayContext.Provider value={replay}>
          <AppShell
            padding="md"
            header={{ height: showTitleBar ? 70 : 0 }}
            aside={{ width: STUDY_BROWSER_WIDTH, breakpoint: 'xs', collapsed: { desktop: !asideOpen, mobile: !asideOpen } }}
            footer={{ height: isAnalysis ? 125 + (hasAudio ? 55 : 0) : 0 }}
            style={{ '--app-shell-aside-offset': '0rem' } as CSSProperties}
          >
            {asideOpen && <AppAside />}
            {showTitleBar && (
            <AppHeader developmentModeEnabled={developmentModeEnabled} dataCollectionEnabled={dataCollectionEnabled} />
            )}
            <DeviceWarning developmentModeEnabled={developmentModeEnabled} />
            {isScreenRecordingUserRejected && <ScreenRecordingRejection />}
            <HelpModal />
            <AlertModal />
            <ConfigVersionWarningModal />
            <Flex direction="row" gap="xs" style={{ width: '100%', maxWidth: rowMaxWidth }}>
              <AppNavBar width={sidebarWidth} top={showTitleBar ? 70 : 0} sidebarOpen={sidebarOpen} />
              {/* 10px is the gap between the sidebar and the main content */}
              <AppShell.Main
                className="main"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                }}
                w={sidebarOpen ? `calc(100% - ${2 * sidebarWidth}px - 20px)` : '100%'}
              >
                {!showTitleBar && !showStudyBrowser && developmentModeEnabled && (
                <Button
                  variant="subtle"
                  leftSection={<IconArrowLeft size={14} />}
                  onClick={() => dispatch(toggleStudyBrowser())}
                  size="xs"
                  style={{ position: 'fixed', top: '10px', right: '10px' }}
                >
                  Study Browser
                </Button>
                )}
                <Outlet />
              </AppShell.Main>
              {sidebarOpen && <Box w={sidebarWidth} miw={sidebarWidth} bg="gray.1" />}
            </Flex>
            {isAnalysis && (
            <AnalysisFooter setHasAudio={setHasAudio} key={currentComponent} />
            )}
          </AppShell>
        </ReplayContext.Provider>
      </RecordingContext.Provider>
    </WindowEventsContext.Provider>
  );
}
