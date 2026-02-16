/**
 * Task Management Widget
 * Shows pending tasks, assignments, and due dates
 */

'use client';

import React, { useState } from 'react';
import { Card, Badge } from '../ui/Cards';

interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'pending_review' | 'completed';
  assignee?: string;
  dueDate: Date;
  controlId?: string;
  riskId?: string;
}

interface TaskWidgetProps {
  tasks: Task[];
  locale: 'ar' | 'en';
  onTaskClick?: (task: Task) => void;
}

export function TaskWidget({ tasks, locale, onTaskClick }: TaskWidgetProps) {
  const [filter, setFilter] = useState<'all' | 'my_tasks' | 'overdue'>('all');

  const getPriorityBadge = (priority: string) => {
    const variants = {
      critical: 'danger' as const,
      high: 'warning' as const,
      medium: 'info' as const,
      low: 'default' as const,
    };
    return variants[priority as keyof typeof variants] || 'default';
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      critical: 'text-red-600',
      high: 'text-orange-600',
      medium: 'text-blue-600',
      low: 'text-gray-600',
    };
    return colors[priority as keyof typeof colors] || 'text-gray-600';
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      open: 'default' as const,
      in_progress: 'info' as const,
      pending_review: 'warning' as const,
      completed: 'success' as const,
    };
    return variants[status as keyof typeof variants] || 'default';
  };

  const formatDueDate = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diff < 0) return locale === 'ar' ? `متأخر ${Math.abs(diff)} يوم` : `${Math.abs(diff)}d overdue`;
    if (diff === 0) return locale === 'ar' ? 'اليوم' : 'Today';
    if (diff === 1) return locale === 'ar' ? 'غداً' : 'Tomorrow';
    return `${diff}${locale === 'ar' ? 'ي' : 'd'}`;
  };

  const isOverdue = (date: Date) => date < new Date();

  const filteredTasks = tasks.filter(task => {
    if (filter === 'overdue') return isOverdue(task.dueDate);
    if (filter === 'my_tasks') return task.assignee; // In real app, check if assignee is current user
    return true;
  });

  const taskCounts = {
    all: tasks.length,
    my_tasks: tasks.filter(t => t.assignee).length,
    overdue: tasks.filter(t => isOverdue(t.dueDate)).length,
  };

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          {locale === 'ar' ? 'المهام والتكليفات' : 'Tasks & Assignments'}
        </h3>
        <button className="px-3 py-1.5 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 transition-colors">
          {locale === 'ar' ? '+ مهمة جديدة' : '+ New Task'}
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-4">
        {(['all', 'my_tasks', 'overdue'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`
              px-3.5 py-2 rounded-md text-sm font-medium transition-all
              ${filter === f 
                ? 'bg-gray-900 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            {locale === 'ar' 
              ? (f === 'all' ? 'الكل' : f === 'my_tasks' ? 'مهامي' : 'المتأخرة')
              : (f === 'all' ? 'All' : f === 'my_tasks' ? 'My Tasks' : 'Overdue')
            }
            <span className={`ml-1.5 px-1.5 py-0.5 rounded-full text-xs ${filter === f ? 'bg-gray-700' : 'bg-gray-300'}`}>
              {taskCounts[f]}
            </span>
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {filteredTasks.map(task => (
          <div
            key={task.id}
            onClick={() => onTaskClick?.(task)}
            className="p-4 border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-sm transition-all cursor-pointer bg-white"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-gray-900 text-sm">{task.title}</h4>
                  <Badge variant={getPriorityBadge(task.priority)} size="sm">
                    {locale === 'ar' 
                      ? (task.priority === 'critical' ? 'حرج' : task.priority === 'high' ? 'عالي' : task.priority === 'medium' ? 'متوسط' : 'منخفض')
                      : task.priority
                    }
                  </Badge>
                </div>
                {task.description && (
                  <p className="text-xs text-gray-600 mb-2">{task.description}</p>
                )}
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  {task.assignee && (
                    <span className="flex items-center gap-1">
                      <span className="text-gray-400">Owner:</span>
                      {task.assignee}
                    </span>
                  )}
                  {task.controlId && (
                    <span className="flex items-center gap-1">
                      <span className="text-gray-400">Control:</span>
                      {task.controlId}
                    </span>
                  )}
                  <span className={`flex items-center gap-1 font-medium ${isOverdue(task.dueDate) ? 'text-red-600' : ''}`}>
                    <span className="text-gray-400">Due:</span>
                    {formatDueDate(task.dueDate)}
                  </span>
                </div>
              </div>
              <Badge variant={getStatusBadge(task.status)} size="sm">
                {locale === 'ar'
                  ? (task.status === 'open' ? 'مفتوح' : task.status === 'in_progress' ? 'قيد التنفيذ' : task.status === 'pending_review' ? 'قيد المراجعة' : 'مكتمل')
                  : task.status.replace('_', ' ')
                }
              </Badge>
            </div>

            {/* Progress Bar for In Progress Tasks */}
            {task.status === 'in_progress' && (
              <div className="mt-2">
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-gray-900 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-sm">{locale === 'ar' ? 'لا توجد مهام' : 'No tasks'}</p>
        </div>
      )}
    </Card>
  );
}
