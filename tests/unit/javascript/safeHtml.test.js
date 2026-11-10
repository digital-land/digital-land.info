import { describe, expect, test } from 'vitest'
import { escapeHtml, safeCssColour, safeOpacity } from '../../../assets/javascripts/safeHtml.js'

describe('escapeHtml', () => {
  test('escapes HTML special characters', () => {
    expect(escapeHtml(`<img src=x onerror="a('b')">&`))
      .toBe('&lt;img src=x onerror=&quot;a(&#39;b&#39;)&quot;&gt;&amp;')
  })

  test('leaves ordinary text alone', () => {
    expect(escapeHtml('Conservation area')).toBe('Conservation area')
  })

  test('handles null, undefined and numbers', () => {
    expect(escapeHtml(null)).toBe('')
    expect(escapeHtml(undefined)).toBe('')
    expect(escapeHtml(42)).toBe('42')
  })
})

describe('safeCssColour', () => {
  test.each(['#abc', '#abcd', '#AABBCC', '#78aa00', '#AABBCC80', 'red', ' #78AA00 '])(
    'accepts %s',
    (colour) => {
      expect(safeCssColour(colour, '#003078')).toBe(colour.trim())
    }
  )

  test.each([
    'red;" onmouseover="alert(1)',
    'red; background: url(https://evil.example)',
    'url(https://evil.example)',
    'expression(alert(1))',
    'javascript:alert(1)',
    'rgb(0, 0, 0)',
    '#12345',
    '',
    null,
    undefined,
    123,
  ])('rejects %s', (colour) => {
    expect(safeCssColour(colour, '#003078')).toBe('#003078')
  })
})

describe('safeOpacity', () => {
  test.each([
    [0.2, 0.2],
    ['0.35', 0.35],
    [0, 0],
    [1, 1],
    [-1, 0],
    [5, 1],
  ])('turns %s into %s', (input, expected) => {
    expect(safeOpacity(input, 0.6)).toBe(expected)
  })

  test.each(['abc', '0.5;" onclick="x', null, undefined, ''])('falls back for %s', (input) => {
    expect(safeOpacity(input, 0.6)).toBe(0.6)
  })
})
