import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch, Router as WouterRouter } from "wouter";
import { getBasePath } from "@/lib/basePath";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import Home from "./pages/Home";
import Login from "./pages/Login";
import UserSettings from "./pages/UserSettings";
import TeacherDashboard from "./pages/TeacherDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import TopicLibrary from "./pages/TopicLibrary";
import WishSubmission from "./pages/WishSubmission";
import MatchResult from "./pages/MatchResult";
import TeacherReview from "./pages/TeacherReview";
import UserManagement from "./pages/UserManagement";
import SystemConfig from "./pages/SystemConfig";
import BulkImport from "./pages/BulkImport";
import YearManagement from "./pages/YearManagement";
import ReviewStatus from "./pages/ReviewStatus";
import Statistics from "./pages/Statistics";
import TeacherStudents from "./pages/TeacherStudents";
import ThesisUpload from "./pages/ThesisUpload";
import SecondTeacherAssignment from "./pages/SecondTeacherAssignment";
import ThesisReview from "./pages/ThesisReview";
import AdminScoreStatistics from "./pages/AdminScoreStatistics";
import TitleChangeRequest from "./pages/TitleChangeRequest";
import TitleChangeReview from "./pages/TitleChangeReview";

import TopicLibraryManagement from "./pages/TopicLibraryManagement";
import ChineseTeacherMonitoring from "./pages/ChineseTeacherMonitoring";
import StudentGuidanceLogs from "./pages/StudentGuidanceLogs";
import TeacherGuidanceLogs from "./pages/TeacherGuidanceLogs";
import StudentPurchaseRequest from "./pages/StudentPurchaseRequest";
import AdminPurchaseManagement from "./pages/AdminPurchaseManagement";
import TeacherPurchaseReview from "./pages/TeacherPurchaseReview";
import AdminProxyImport from "./pages/AdminProxyImport";
import AdminUserActivityLogs from "./pages/AdminUserActivityLogs";

function AppRouter() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/login" component={Login} />
      <Route path="/settings" component={UserSettings} />
      <Route path="/teacher" component={TeacherDashboard} />
      <Route path="/teacher/topics" component={TopicLibrary} />
      <Route path="/teacher/review" component={TeacherReview} />
      <Route path="/teacher/students" component={TeacherStudents} />
      <Route path="/teacher/thesis-review" component={ThesisReview} />
      <Route path="/teacher/title-change" component={TitleChangeReview} />

      <Route path="/teacher/guidance" component={TeacherGuidanceLogs} />
      <Route path="/teacher/purchase" component={TeacherPurchaseReview} />
      <Route path="/student" component={StudentDashboard} />
      <Route path="/student/topics" component={WishSubmission} />
      <Route path="/student/wishes" component={WishSubmission} />
      <Route path="/student/thesis" component={ThesisUpload} />
      <Route path="/student/title-change" component={TitleChangeRequest} />
      <Route path="/student/guidance" component={StudentGuidanceLogs} />
      <Route path="/student/purchase" component={StudentPurchaseRequest} />
      <Route path="/admin" component={AdminDashboard} />
      <Route path="/admin/users" component={UserManagement} />
      <Route path="/admin/import" component={BulkImport} />
      <Route path="/admin/config" component={SystemConfig} />
      <Route path="/admin/matches" component={MatchResult} />
      <Route path="/admin/stats" component={Statistics} />
      <Route path="/admin/years" component={YearManagement} />
      <Route path="/admin/review-status" component={ReviewStatus} />
      <Route path="/admin/second-teacher" component={SecondTeacherAssignment} />
      <Route path="/admin/score-statistics" component={AdminScoreStatistics} />
      <Route path="/admin/topic-library" component={TopicLibraryManagement} />
      <Route path="/admin/chinese-teacher-monitoring" component={ChineseTeacherMonitoring} />
      <Route path="/admin/purchase" component={AdminPurchaseManagement} />
      <Route path="/admin/proxy-import" component={AdminProxyImport} />
      <Route path="/admin/activity-logs" component={AdminUserActivityLogs} />
      <Route path="/404" component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  const basePath = getBasePath(); // 实例1: ""  实例2: "/instance2"
  return (
    <ErrorBoundary>
      <WouterRouter base={basePath}>
        <ThemeProvider defaultTheme="light">
          <LanguageProvider>
            <TooltipProvider>
              <Toaster />
              <AppRouter />
            </TooltipProvider>
          </LanguageProvider>
        </ThemeProvider>
      </WouterRouter>
    </ErrorBoundary>
  );
}

export default App;
