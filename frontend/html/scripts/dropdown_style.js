// Select -> CustomSelect enhancer
(function () {
  function enhanceSelect(select) {
    if (select.dataset.enhanced) return;
    select.dataset.enhanced = "1";
    select.style.display = "none";

    const wrapper = document.createElement('div');
    wrapper.className = 'custom-select';
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'trigger';
    trigger.setAttribute('aria-haspopup', 'listbox');
    trigger.setAttribute('aria-expanded', 'false');

    const label = document.createElement('span');
    label.className = 'label';
    label.textContent = select.options[select.selectedIndex]?.text || '';

    const arrow = document.createElement('span');
    arrow.className = 'arrow';

    trigger.appendChild(label);
    trigger.appendChild(arrow);

    const optionsList = document.createElement('div');
    optionsList.className = 'custom-options';
    optionsList.setAttribute('role', 'listbox');

    // build options
    Array.from(select.options).forEach((opt, idx) => {
      const item = document.createElement('div');
      item.className = 'custom-option';
      item.setAttribute('data-value', opt.value);
      item.setAttribute('role', 'option');
      item.textContent = opt.text;
      if (opt.disabled) item.setAttribute('aria-disabled', 'true');
      if (idx === select.selectedIndex) item.classList.add('selected');

      item.addEventListener('click', () => {
        // update original select
        select.value = opt.value;
        select.dispatchEvent(new Event('input', { bubbles: true }));
        select.dispatchEvent(new Event('change', { bubbles: true }));
        // update UI
        optionsList.querySelectorAll('.custom-option').forEach(o => o.classList.remove('selected'));
        item.classList.add('selected');
        label.textContent = opt.text;
        close();
      });

      optionsList.appendChild(item);
    });

    wrapper.appendChild(trigger);
    wrapper.appendChild(optionsList);
    select.parentNode.insertBefore(wrapper, select.nextSibling);

    function open() {
      wrapper.classList.add('open');
      trigger.setAttribute('aria-expanded', 'true');
      // focus first selected or first item
      const sel = optionsList.querySelector('.custom-option.selected') || optionsList.querySelector('.custom-option');
      sel && sel.focus && sel.focus();
    }
    function close() {
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', 'false');
    }

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      if (wrapper.classList.contains('open')) close();
      else open();
    });

    // keyboard navigation
    let focusedIdx = -1;
    trigger.addEventListener('keydown', (e) => {
      const items = Array.from(optionsList.querySelectorAll('.custom-option'));
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!wrapper.classList.contains('open')) { open(); focusedIdx = 0; items[0].focus(); return; }
        focusedIdx = Math.min(items.length - 1, (focusedIdx < 0 ? 0 : focusedIdx + 1));
        items[focusedIdx].focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (!wrapper.classList.contains('open')) { open(); focusedIdx = items.length - 1; items[focusedIdx].focus(); return; }
        focusedIdx = Math.max(0, focusedIdx - 1);
        items[focusedIdx].focus();
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        if (!wrapper.classList.contains('open')) open();
        else {
          const focused = document.activeElement;
          focused && focused.classList.contains('custom-option') && focused.click();
        }
      } else if (e.key === 'Escape') {
        close();
        trigger.focus();
      }
    });

    // ensure each option is focusable for keyboard navigation
    optionsList.querySelectorAll('.custom-option').forEach((el, i) => {
      el.tabIndex = 0;
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); el.click(); }
        if (e.key === 'Escape') { close(); trigger.focus(); }
        if (e.key === 'ArrowDown') { e.preventDefault(); const next = el.nextElementSibling; if (next) next.focus(); }
        if (e.key === 'ArrowUp') { e.preventDefault(); const prev = el.previousElementSibling; if (prev) prev.focus(); }
      });
    });

    // close on outside click
    document.addEventListener('click', (ev) => {
      if (!wrapper.contains(ev.target)) close();
    });
  }

  // convert all selects with class .select
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('select.select').forEach(enhanceSelect);
  });

  document.addEventListener("force-enhance-select", (e) => {
  enhanceSelect(e.detail);
});



})();
