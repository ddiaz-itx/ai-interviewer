import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import CreateInterview from './CreateInterview';
import { BrowserRouter } from 'react-router-dom';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

// Mock apiClient to avoid issues with import or undefined calls
vi.mock('../api/client', () => ({
    apiClient: {
        createInterview: vi.fn(),
        uploadDocuments: vi.fn(),
    },
}));

describe('CreateInterview', () => {
    beforeEach(() => {
        mockNavigate.mockClear();
    });

    test('renders Back to Dashboard button', () => {
        render(
            <BrowserRouter>
                <CreateInterview />
            </BrowserRouter>
        );
        const backButton = screen.getByText(/Back to Dashboard/i);
        expect(backButton).toBeInTheDocument();
    });

    test('navigates to dashboard when back button is clicked', () => {
        render(
            <BrowserRouter>
                <CreateInterview />
            </BrowserRouter>
        );
        const backButton = screen.getByText(/Back to Dashboard/i);
        fireEvent.click(backButton);
        expect(mockNavigate).toHaveBeenCalledWith('/admin');
    });
});
