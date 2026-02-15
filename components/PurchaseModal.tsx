'use client'

import { useState, useEffect } from 'react'
import styles from './PurchaseModal.module.css'

interface Workflow {
  workflow_id: string
  title: string
  description: string
  price_tokens: number
  tokens_saved: number
  savings_percentage: number
  rating: number
  pricing?: {
    base_price: number
    quality_multiplier: number
    roi_percentage: number
    breakdown: string
  }
}

interface PurchaseModalProps {
  workflow: Workflow
  onClose: () => void
  onSuccess: (receipt: any) => void
  apiBase: string
}

type ModalState = 'confirm' | 'processing' | 'success' | 'error'

export default function PurchaseModal({ workflow, onClose, onSuccess, apiBase }: PurchaseModalProps) {
  const [state, setState] = useState<ModalState>('confirm')
  const [balance, setBalance] = useState<number | null>(null)
  const [receipt, setReceipt] = useState<any>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    // Fetch user balance
    fetch(`${apiBase}/api/commerce/balance?user_id=default_user`)
      .then((r) => r.json())
      .then((data) => setBalance(data.balance ?? 5000))
      .catch(() => setBalance(5000))
  }, [apiBase])

  const handlePurchase = async () => {
    setState('processing')
    try {
      const res = await fetch(`${apiBase}/api/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflow.workflow_id,
          user_id: 'default_user',
        }),
      })

      const data = await res.json()

      if (!res.ok || !data.success) {
        setError(data.error || 'Purchase failed. Please try again.')
        setState('error')
        return
      }

      setReceipt(data.receipt || data)
      setState('success')
      onSuccess(data)
      // Notify wallet to refresh balance
      window.dispatchEvent(new Event('wallet-refresh'))
    } catch (err) {
      setError('Network error. Please check your connection and try again.')
      setState('error')
    }
  }

  const insufficientBalance = balance !== null && balance < workflow.price_tokens

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Close button */}
        <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
          ✕
        </button>

        {/* ── CONFIRM STATE ── */}
        {state === 'confirm' && (
          <>
            <div className={styles.header}>
              <div className={styles.iconWrap}>
                <span className={styles.icon}>◈</span>
              </div>
              <h2 className={styles.title}>Confirm Purchase</h2>
            </div>

            <div className={styles.workflowInfo}>
              <div className={styles.workflowName}>{workflow.title}</div>
              <p className={styles.workflowDesc}>{workflow.description}</p>
            </div>

            <div className={styles.priceRow}>
              <div className={styles.priceDetail}>
                <span className={styles.priceDetailLabel}>Price</span>
                <span className={styles.priceDetailValue}>
                  <span className={styles.tokenSymbol}>◈</span>
                  {workflow.price_tokens.toLocaleString()} tokens
                </span>
              </div>
              <div className={styles.priceDetail}>
                <span className={styles.priceDetailLabel}>Your Balance</span>
                <span className={`${styles.priceDetailValue} ${insufficientBalance ? styles.insufficientBalance : ''}`}>
                  <span className={styles.tokenSymbol}>◈</span>
                  {balance !== null ? balance.toLocaleString() : '…'} tokens
                </span>
              </div>
            </div>

            {workflow.tokens_saved > 0 && (
              <div className={styles.savingsBanner}>
                <span className={styles.savingsIcon}>↓</span>
                <span>
                  Save <strong>{workflow.tokens_saved.toLocaleString()}</strong> tokens per use ({workflow.savings_percentage}% reduction)
                </span>
              </div>
            )}

            {insufficientBalance && (
              <div className={styles.errorBanner}>
                Insufficient balance. You need {(workflow.price_tokens - (balance || 0)).toLocaleString()} more tokens.
              </div>
            )}

            <div className={styles.actions}>
              <button className={styles.btnCancel} onClick={onClose}>
                Cancel
              </button>
              <button
                className={styles.btnConfirm}
                onClick={handlePurchase}
                disabled={insufficientBalance || balance === null}
              >
                Purchase for ◈ {workflow.price_tokens.toLocaleString()}
              </button>
            </div>
          </>
        )}

        {/* ── PROCESSING STATE ── */}
        {state === 'processing' && (
          <div className={styles.stateContainer}>
            <div className={styles.spinner} />
            <h2 className={styles.stateTitle}>Processing Purchase…</h2>
            <p className={styles.stateText}>Verifying balance and completing transaction.</p>
          </div>
        )}

        {/* ── SUCCESS STATE ── */}
        {state === 'success' && (
          <div className={styles.stateContainer}>
            <div className={styles.successIcon}>✓</div>
            <h2 className={styles.stateTitle}>Purchase Complete!</h2>
            <p className={styles.stateText}>
              You now own <strong>{workflow.title}</strong>.
            </p>

            {receipt && (
              <div className={styles.receiptCard}>
                <div className={styles.receiptRow}>
                  <span>Transaction</span>
                  <span className={styles.receiptCode}>{receipt.tx_id}</span>
                </div>
                <div className={styles.receiptRow}>
                  <span>Amount</span>
                  <span>◈ {(receipt.cost || workflow.price_tokens).toLocaleString()}</span>
                </div>
                <div className={styles.receiptRow}>
                  <span>New Balance</span>
                  <span>◈ {(receipt.new_balance ?? '—').toLocaleString()}</span>
                </div>
              </div>
            )}

            <button className={styles.btnConfirm} onClick={onClose}>
              Done
            </button>
          </div>
        )}

        {/* ── ERROR STATE ── */}
        {state === 'error' && (
          <div className={styles.stateContainer}>
            <div className={styles.errorIcon}>!</div>
            <h2 className={styles.stateTitle}>Purchase Failed</h2>
            <p className={styles.stateText}>{error}</p>
            <div className={styles.actions}>
              <button className={styles.btnCancel} onClick={onClose}>
                Close
              </button>
              <button className={styles.btnConfirm} onClick={() => setState('confirm')}>
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
