import 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    _skipAuth?: boolean;
    _retry?: boolean;
  }
}
